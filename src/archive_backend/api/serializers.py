from .abstract_remote_serializer import AbstractRemoteSerializer
from archive_backend.models import *
from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

class RemotePeerSerializer(AbstractRemoteSerializer):
    class Meta:
        model = RemotePeer
        exclude = ["is_this_site", "mirror_files", "last_checkin"]

class LanguageSerializer(AbstractRemoteSerializer):
    class Meta:
        model = Language
        exclude = ["alias_identifier"]

class FileFormatSerializer(AbstractRemoteSerializer):
    class Meta:
        model = FileFormat
        exclude = ["alias_identifier"]

class AuthorSerializer(AbstractRemoteSerializer):
    class Meta:
        model = Author
        exclude = ["alias_identifier"]

class AuthorDescriptionTranslationSerializer(AbstractRemoteSerializer):
    class Meta:
        model = AuthorDescriptionTranslation
        fields = "__all__"

class AbstractDocumentSerializer(AbstractRemoteSerializer):
    class Meta:
        model = AbstractDocument
        exclude = ["alias_identifier"]

class AbstractDocumentDescriptionTranslationSerializer(AbstractRemoteSerializer):
    class Meta:
        model = AbstractDocumentDescriptionTranslation
        fields = "__all__"

class EditionSerializer(AbstractRemoteSerializer):
    class Meta:
        model = Edition
        exclude = ["actively_generated_from", "generation_config"]



rs = RevisionStatus
#first level index, old, next level array of remote, 
RevisionTransitions = {
    rs.ONDISKPUBLISHED: {
        "default": rs.ONDISKPUBLISHED
    },
    rs.JOBSCHEDULED: {
        frozenset([rs.ONDISKPUBLISHED, rs.JOBSCHEDULED, rs.REMOTEJOBSCHEDULED]): rs.JOBSCHEDULED,
        "default": IntegrityError("Revision was in JOBSCHEDULED state, but the remote status was not ONDISKPUBLISHED, JOBSCHEDULED or REMOTEJOBSCHEDULED")
    },
    rs.REQUESTABLE: {
        frozenset([rs.ONDISKPUBLISHED]): rs.REQUESTABLE,
        "default": IntegrityError("Revision was in REQUESTABLE state, but the remote status was not ONDISKPUBLISHED")
    },
    rs.REMOTEJOBSCHEDULED: {
        frozenset([rs.ONDISKPUBLISHED]): rs.REQUESTABLE,
        frozenset([rs.JOBSCHEDULED, rs.REMOTEJOBSCHEDULED]): rs.REMOTEJOBSCHEDULED,
        "default": IntegrityError("Revision was in REMOTEJOBSCHEDULED state, but the remote status was not ONDISKPUBLISHED, JOBSCHEDULED or REMOTEJOBSCHEDULED")
    },
    rs.REMOTEREQUESTABLE: {#Also use this case for new items
        frozenset([rs.ONDISKPUBLISHED]): rs.REQUESTABLE,
        frozenset([rs.JOBSCHEDULED, rs.REMOTEJOBSCHEDULED]): rs.REMOTEJOBSCHEDULED,
        frozenset([rs.REQUESTABLE, rs.REMOTEREQUESTABLE]): rs.REMOTEREQUESTABLE,
        "default": Exception("Unhandled status transition")
    } 
}

def get_next_status(old_status, remote_status):
    if old_status is None: #new item has identical status transition results as REMOTEREQUESTABLE
        return get_next_status(rs.REMOTEREQUESTABLE, remote_status)
    
    new_val = None

    for (key, value) in RevisionTransitions[old_status].items():
        if key == "default":
            continue
        if remote_status in key:
            new_val = value

    if new_val is None:
        new_val = RevisionTransitions[old_status]["default"]

    if issubclass(Exception, new_val.__class__):
        raise Exception(f" (old_status: {old_status}, remote_status: {remote_status})") from new_val
    return new_val
        

class RevisionSerializer(AbstractRemoteSerializer):
    
    def validate_status(self, value_on_remote):
        """Transforms the status of a revision to the correct status based on the current status (if the object already exists locally) and the remote status.
        
        eg. If the current local status is ONDISKPUBLISHED and the remote status is REQUESTABLE, the status will stay ONDISKPUBLISHED.
        
        If the remote status is ONDISKPUBLISHED, the local status will be set to REQUESTABLE, unless it was already JOBSCHEDULED.
        
        etc."""
        old_status = self.initial_data.get("id", None)
        if old_status is not None:
            old_status = Revision.objects.get(id=old_status).status

        if old_status is RevisionStatus.UNFINISHED or value_on_remote is RevisionStatus.UNFINISHED:
            raise IntegrityError("Cannot set status to UNFINISHED or overwrite an UNFINISHED status")
        
        return get_next_status(old_status, value_on_remote)

    class Meta:
        model = Revision
        exclude = ["generated_from"]

class PersistentIdSerializer(serializers.ModelSerializer):
    # def to_internal_value(self, data):
    #     id = data["id"]
    #     try:
    #         return PersistentFileID.objects.get(id)
    #     except ObjectDoesNotExist:
    #         return PersistentFileID.objects.create(id = id)
        
    class Meta:
        model = PersistentFileID
        fields = "__all__"

class ArchiveFileSerializer(AbstractRemoteSerializer):
    # persistent_file_ids = PersistentIdSerializer(many=True)

    class Meta:
        model = ArchiveFile
        exclude = ["file"]
