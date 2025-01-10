
from django.db import models
from django.db.models import Subquery

#Untested, is this even needed?

class AliasQuerySet(models.QuerySet):
   def aliases(self):
        """Returns all aliases of the queryset."""
        return self.model.objects.filter(alias_origin_end__alias_identifier__in=
                               Subquery(self.values('alias_origin_end__alias_identifier').distinct()))