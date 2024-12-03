from logging import warning


def AliasSuggestionSignal(sender, instance, action, reverse, model, pk_set, **kwargss):
    # A query that checks if the unprocessed alias suggestions are not a subset of a previously rejected set. 
    # Also checks if the unprocessed items arent already aliased
    # Removes suggestion if it is.
    # Manually registered in the generic alias suggestion model call
    if action == "post_add":
        rejected_subset = (instance.__class__.objects
                .annotate(matching_rejected=Count('rejected', filter=Q(rejected__in=set(instance.unprocessed.all()))))
                .filter(matching_rejected=instance.unprocessed.all().count()))
        approved_subset = (instance.__class__.objects
                .annotate(matching_approved=Count('approved', filter=Q(approved__in=set(instance.unprocessed.all()))))
                .filter(matching_approved=instance.unprocessed.all().count()))
        oldunprocessed_subset = (instance.__class__.objects
                .annotate(matching_oldunprocessed=Count('oldunprocessed', filter=Q(oldunprocessed__in=set(instance.unprocessed.all()))))
                .filter(matching_oldunprocessed=instance.unprocessed.all().count()))

        aliasIdentifiers = set([x.alias_identifier for x in instance.unprocessed])

        if rejected_subset.count() > 0 or approved_subset.count() > 0 or oldunprocessed_subset.count() > 0 or len(aliasIdentifiers) == 1:
            # The suggested merge is already a subset of
                # A rejected suggestion set, so we dont need to suggest it again.
                # An approved suggestion set, so it should already be handled (indicated faulty db state).
                # An old unprocessed suggestion set, so it is already pending.
            # Or all unprocessed items have the same identifier and thus are already aliased
            if approved_subset.count() > 0:
                warning.warn("The suggested merge is already a subset of a previous approved merge, possibly indicating that the suggestion database is out of sync and should be refreshed.")
            alias_suggestions = instance.__class__.objects.filter(pk=instance.pk)
            alias_suggestions.delete()