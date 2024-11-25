from rest_framework import serializers

from archivebackend.models import RemotePeer, Revision

class RemoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RemotePeer
        fields = ["from_remote", "id", "site_name", "site_adress"]

class RevisionSerializer(serializers.ModelSerializer):
    from_remote = RemoteSerializer()

    class Meta:
        model = Revision
        fields =  ["from_remote", "id", 'is_backup_revision', 'belongs_to', 'date', 'entry_file', 'status', 'files']