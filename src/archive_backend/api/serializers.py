from .abstract_remote_serializer import AbstractRemoteSerializer
from archive_backend.models import *

class RemotePeerSerializer(AbstractRemoteSerializer):
    class Meta:
        model = RemotePeer
        exclude = ["is_this_site", "mirror_files", "last_checkin"]

class LanguageSerializer(AbstractRemoteSerializer):
    from_remote = RemotePeerSerializer()

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

class RevisionSerializer(AbstractRemoteSerializer):

    def validate_status(self, value):
        """Validate remote status"""
        #TODO implement and change validated status to be appropriate for this (ie if it read "job scheduled" from remote, it should be "remote job scheduled" in this database)
        raise NotImplementedError()

    class Meta:
        model = Revision
        exclude = ["generated_from"]

class ArchiveFileSerializer(AbstractRemoteSerializer):
    def validate_file(self, value):
        #TODO
        raise NotImplementedError()

    class Meta:
        model = ArchiveFile
        exclude = ["file"]
