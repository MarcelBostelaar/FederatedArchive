from rest_framework import serializers

from ArchiveBackend.models import RemotePeer, Revision

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemotePeer
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        exclude = kwargs.pop('exclude', [])  # Get `exclude` from kwargs
        super().__init__(*args, **kwargs)

        if exclude:
            for field in exclude:
                self.fields.pop(field)

class RemoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemotePeer
        fields = ["from_remote", "id", "site_name", "site_adress"]

class RevisionSerializer(serializers.ModelSerializer):
    from_remote = RemoteSerializer()

    class Meta:
        model = Revision
        fields =  ["from_remote", "id", 'is_backup_revision', 'belongs_to', 'date', 'entry_file', 'status', 'files']