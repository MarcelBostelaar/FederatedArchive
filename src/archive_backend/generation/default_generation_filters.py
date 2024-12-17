import datetime
from archive_backend.models import Revision, Edition
from archive_backend.models.revision import RevisionStatus
from archive_backend.utils.timeparser import timeparse

def create_generated_revision(source: Revision, for_edition: Edition):
    Revision.objects.create(
        belongs_to = for_edition,
        status = RevisionStatus.REQUESTABLE,
        generated_from = source
    )

def always(edition: Edition):
    parent_edition = edition.actively_generated_from
    parent_revisions = parent_edition.revisions.filter(status_ne = RevisionStatus.UNFINISHED)
    own_revisions = edition.revisions.all()
    for parent_rev in parent_revisions:
        if not own_revisions.filter(generated_from = parent_rev).exists():
            create_generated_revision(parent_rev, edition)

def for_backups(edition: Edition):
    parent_edition = edition.actively_generated_from
    parent_revisions = parent_edition.revisions.filter(status_ne = RevisionStatus.UNFINISHED).filter(is_backup = True)
    own_revisions = edition.revisions.all()
    for parent_rev in parent_revisions:
        if not own_revisions.filter(generated_from = parent_rev).exists():
            create_generated_revision(parent_rev, edition)

def if_no_revision_younger_than(edition: Edition):
    genconfigjson = edition.generation_config.config_json
    min_age = timeparse(genconfigjson.get('previous_revision_age', "1000y1d1h1m1s"))
    limit = datetime.now() - min_age
    parent_edition = edition.actively_generated_from
    parent_revisions = parent_edition.revisions.filter(status_ne = RevisionStatus.UNFINISHED).order_by('-date')
    if parent_revisions.count() == 0:
        return #Nothing to generate from
    parent_revision = parent_revisions.first()
    valid_own_revisions = edition.revisions.filter(date_gt = limit).count()
    if valid_own_revisions > 0:
        return #condition satisfied
    create_generated_revision(parent_revision, edition)
