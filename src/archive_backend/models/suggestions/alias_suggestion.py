from logging import warning
from django.db import models
from django.db.models import Count, Q
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from archive_backend.models.file_format import FileFormat

class SuggestionStatus(models.IntegerChoices):
    unprocessed = 0
    rejected = 1
    accepted = 2

class SuggestedAction(models.Model):
    """Table containing suggested actions to approve or disapprove."""
    title = models.CharField(max_length=255, default="No title", blank=True)
    description = models.TextField(default="No description provided.", blank=True)
    creation = models.DateTimeField(auto_now_add=True, blank=True)
    status = models.IntegerField(choices=SuggestionStatus.choices, default=SuggestionStatus.unprocessed)

    def execute_suggestion(self):
        raise NotImplementedError("execute_suggestion must be implemented by subclasses.")

    class Meta:
        abstract = True

class SuggestionFieldAlias(SuggestedAction):
    unprocessed = models.ManyToManyField(FileFormat, related_name="+", blank=True)
    rejected = models.ManyToManyField(FileFormat, related_name="+", blank=True)
    accepted = models.ManyToManyField(FileFormat, related_name="+", blank=True)

    def post_execution(self):
        #TODO filter unprocessed to check if they are already part of the same alias group
        if self.unprocessed.count() > 0:
            self.__class__(unprocessed=self.unprocessed).save()
        if self.rejected.count() > 0:
            self.__class__(rejected=self.rejected).save()
        if self.accepted.count() > 0:
            self.__class__(accepted=self.accepted).save()
        self.delete()
    
    def execute_suggestion(self):
        if self.accepted.count() > 1:
            items = list(self.accepted.all())
            first = items.pop(0)
            for x in items:
                first.addAlias(x)
        self.post_execution()


@receiver(m2m_changed, sender=SuggestionFieldAlias.unprocessed.through)
def AliasSuggestionSignal(sender, instance, action, reverse, model, pk_set, **kwargss):
    # A query that checks if the unprocessed alias suggestions are not a subset of a previously rejected set. Removes suggestion if it is.
    if action == "post_add":
        rejected_subset = (SuggestionFieldAlias.objects
                .annotate(matching_rejected=Count('rejected', filter=Q(rejected__in=set(instance.unprocessed.all()))))
                .filter(matching_rejected=instance.unprocessed.all().count()))
        approved_subset = (SuggestionFieldAlias.objects
                .annotate(matching_approved=Count('approved', filter=Q(approved__in=set(instance.unprocessed.all()))))
                .filter(matching_approved=instance.unprocessed.all().count()))
        oldunprocessed_subset = (SuggestionFieldAlias.objects
                .annotate(matching_oldunprocessed=Count('oldunprocessed', filter=Q(oldunprocessed__in=set(instance.unprocessed.all()))))
                .filter(matching_oldunprocessed=instance.unprocessed.all().count()))
        if rejected_subset.count() > 0 or approved_subset.count() > 0 or oldunprocessed_subset.count() > 0:
            # The suggested merge is already a subset of
                # A rejected suggestion set, so we dont need to suggest it again.
                # An approved suggestion set, so it should already be handled (indicated faulty db state).
                # An old unprocessed suggestion set, so it is already pending.
            if approved_subset.count() > 0:
                warning.warn("The suggested merge is already a subset of a previous approved merge, possibly indicating that the suggestion database is out of sync and should be refreshed.")
            alias_suggestions = SuggestionFieldAlias.objects.filter(pk=instance.pk)
            alias_suggestions.delete()