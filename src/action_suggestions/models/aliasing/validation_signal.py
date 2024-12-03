from logging import warning
import warnings
from django.db.models import Count, Q


def AliasSuggestionSignal(sender, instance, action, reverse, model, pk_set, **kwargss):
    # A query that checks if the unprocessed alias suggestions are not a subset of a previously rejected set. 
    # Also checks if the unprocessed items arent already aliased
    # Removes suggestion if it is.
    # Manually registered in the generic alias suggestion model call
    if action == "post_add":
        #if all sets are empty, invalid, delete
        #if any set is one, invalid, delete
        #if all items in unprocessed are already aliased, delete
        #if unprocessed is subset of previously rejected/approved/unprocessed, item is unneccecary, delete
        #if rejected is subset of previously accepted, invalid command, ???
        #if rejected is subset of previously rejected, item can be kept
        #if rejected is subset of existing unprocessed, its fine
        #if accepted is subset of previously accepted, item can be kept
        #if accepted is subset of previously rejected, delete previously rejected suggestion
        #if accepted is subset of unprocessed somewhere else, item can be kept
        item_to_delete = instance.__class__.objects.filter(pk=instance.pk)

        if instance.accepted.count() == 0 and instance.rejected.count() == 0 and instance.unprocessed.count() == 0:
            item_to_delete.delete()
            return
        
        if instance.accepted.count() == 1 or instance.rejected.count() == 1 or instance.unprocessed.count() == 1:
            item_to_delete.delete()
            return
        
        aliasIdentifiers = set([x.alias_identifier for x in instance.unprocessed])
        if len(aliasIdentifiers) == 1:
            item_to_delete.delete()
            return
        
        #TODO properly implement some tests, tell admins to clear suggestions and regenerate them if needed
        warnings.warning("Not implemented proper validation for usefullness of alias model")

        rejected_subset = (instance.__class__.objects
                .annotate(matching_rejected=Count('rejected', filter=Q(rejected__in=set(instance.unprocessed.all()))))
                .filter(matching_rejected=instance.unprocessed.all().count()))
        approved_subset = (instance.__class__.objects
                .annotate(matching_approved=Count('accepted', filter=Q(accepted__in=set(instance.unprocessed.all()))))
                .filter(matching_approved=instance.unprocessed.all().count()))
        unprocessed_subset = (instance.__class__.objects
                .annotate(matching_unprocessed=Count('unprocessed', filter=Q(unprocessed__in=set(instance.unprocessed.all()))))
                .filter(matching_unprocessed=instance.unprocessed.all().count()))


        if rejected_subset.count() > 0 or approved_subset.count() > 0 or unprocessed_subset.count() > 0:
            # The suggested merge is already a subset of
                # A rejected suggestion set, so we dont need to suggest it again.
                # An approved suggestion set, so it should already be handled (indicated faulty db state).
                # An old unprocessed suggestion set, so it is already pending.
            if approved_subset.count() > 0:
                warning.warn("The suggested merge is already a subset of a previous approved merge, possibly indicating that the suggestion database is out of sync and should be refreshed.")
            alias_suggestions = instance.__class__.objects.filter(pk=instance.pk)
            alias_suggestions.delete()
            return