from uuid import UUID
from django.urls import path
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import ListAPIView
from django.apps import apps
from datetime import datetime

from django.db.models import Q
from rest_framework import serializers

from archive_backend.models import RemoteModel
from archive_backend.utils.small import registry


class RemoteViewDataContainer:
    def __init__(self, model_serializer, subpath = "", RemoteViewset = None):
        """
        :param model_serializer: The serializer for the model that the viewset will be based on
        :param subpath: The path that the viewset will be mounted on
        :param RemoteViewset: The viewset that will be used. If None, a default viewset (RemoteViewsetFactory) will be created
        """
        ViewContainerRegistry.register(model_serializer.Meta.model, self)
        model = model_serializer.Meta.model
        self.model_name = model.__name__
        model_name_lower = model.__name__.lower()
        if RemoteViewset is None:
            RemoteViewset = RemoteViewsetFactory(model_serializer)
        author_list = RemoteViewset.as_view({'get':'list'})
        author_detail = RemoteViewset.as_view({'get':'retrieve'})

        self._list_url = subpath + model_name_lower
        self._detail_url = f"{subpath}{model_name_lower}/pk/"
        self.paths = [path(self._list_url, author_list, name=f"{model_name_lower}-list"),
                    path(self._detail_url + "<uuid:pk>", author_detail, name=f"{model_name_lower}-detail")]
    
    @staticmethod
    def _generate_url(on_site, url, **kwargs):
        args = "?" + "&".join([f"{key}={value}" for key, value in kwargs.items() if value != ""])
        return f"{on_site}/{url}{args}"

    def get_list_url(self, on_site = "", json_format = True, updated_after: datetime = None):
        return self._generate_url(on_site, self._list_url, 
                                  updated_after=updated_after.isoformat() if updated_after else "", 
                                  format="json" if json_format else "")

    def get_detail_url(self, primary_key: UUID, on_site = "", json_format = True):
        return self._generate_url(on_site, self._list_url + str(primary_key), 
                                  format="json" if json_format else "")

class AliasViewDataContainer(RemoteViewDataContainer):
    def __init__(self, model_serializer, subpath = "", RemoteVieset = None, AliasView = None):
        """
        :param model_serializer: The serializer for the model that the viewset will be based on
        :param subpath: The path that the viewset will be mounted on
        :param RemoteViewset: The viewset that will be used. If None, a default viewset (RemoteViewsetFactory) will be created
        :param AliasView: The view that will be used for the alias view. If None, a default view (AliasSerializerFactory) will be created
        """
        super().__init__(model_serializer, subpath=subpath, RemoteViewset=RemoteVieset)
        ViewContainerRegistry.override(model_serializer.Meta.model, self)
        model = model_serializer.Meta.model
        model_name = model.__name__.lower()
        if AliasView is None:
            AliasView = AliasViewFactory(model_serializer)
        alias_list = AliasView.as_view()

        self._alias_url = f"{subpath}{model_name}/alias"
        self.paths = self.paths + [path(self._alias_url, alias_list, name=f"{model_name}-alias")]

    def get_alias_url(self, on_site = "", json_format = True, related_to:UUID = None):
        return self._generate_url(on_site, self._list_url,
                                  format="json" if json_format else "",
                                  related_to=str(related_to) if related_to is not None else "")

def _AliasSerializerFactory(alias_model):
    class _ThoughSerializer(serializers.ModelSerializer):
        class Meta:
            model = alias_model
            fields = ['origin', 'target']
    return _ThoughSerializer

def RemoteViewsetFactory(model_serializer):
    class RemoteItemViewset(ReadOnlyModelViewSet):
        queryset = model_serializer.Meta.model.objects.all()
        serializer_class = model_serializer
        
        def get_queryset(self):
            the_set = super().get_queryset()
            updated_after = self.request.query_params.get('updated_after', None)
            if updated_after:
                date = datetime.fromisoformat(updated_after)
                the_set = the_set.filter(last_updated__gt=date)
            return the_set
    return RemoteItemViewset

def AliasViewFactory(model_serializer):
    remote_model = apps.get_model('archive_backend.' + model_serializer.Meta.model.__name__ + "AliasThrough")
    class AbstractAliasView(ListAPIView):
        queryset = remote_model.objects.all()
        serializer_class = _AliasSerializerFactory(remote_model)

        def get_queryset(self):
            the_set = super().get_queryset()
            related_to = self.request.query_params.get('related_to', None)
            if related_to is not None:
                the_set = the_set.filter(Q(origin__id=related_to) | Q(target__id=related_to))
            return the_set
    return AbstractAliasView

ViewDataContainer = RemoteViewDataContainer | AliasViewDataContainer
ViewContainerRegistry = registry[RemoteModel, ViewDataContainer]()