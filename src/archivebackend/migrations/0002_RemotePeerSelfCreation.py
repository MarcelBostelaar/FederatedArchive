from django.db import migrations


def makeNewPeer(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    RemotePeer = apps.get_model("archivebackend", "RemotePeer")
    newPeer = RemotePeer()
    newPeer.site_name = "Change this - your site here"
    newPeer.site_adress = "0.0.0.0/CHANGETHIS"
    newPeer.mirror_files = False
    newPeer.peers_of_peer = False
    newPeer.is_this_site = True
    newPeer.save()
    newPeer.from_remote = newPeer
    newPeer.save()


class Migration(migrations.Migration):
    dependencies = [
        ("archivebackend", "0001_RemotePeerInitial"),
    ]

    operations = [
        migrations.RunPython(makeNewPeer),
    ]