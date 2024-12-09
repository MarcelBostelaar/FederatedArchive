import datetime
from archive_backend.models import Revision, Edition
from archive_backend.utils.timeparser import timeparse


def always_true_filter(targetEdition: Edition, sourceRevision: Revision, generation_config: dict):
    return True

def on_backups_filter(targetEdition: Edition, sourceRevision: Revision, generation_config: dict):
    return sourceRevision.is_backup

def if_no_revision_younger_than_filter(targetEdition: Edition, sourceRevision: Revision, generation_config: dict):
    min_age = timeparse(generation_config.get('previous_revision_age', "1000y1d1h1m1s"))
    limit = datetime.now() - min_age
    return not targetEdition.revisions.exclude(date__gt=limit).exists()
