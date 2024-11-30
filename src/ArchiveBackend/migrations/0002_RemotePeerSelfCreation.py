from django.db import migrations


def makeNewPeer(apps, schema_editor):
    RemotePeer = apps.get_model("ArchiveBackend", "RemotePeer")
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
        ("ArchiveBackend", "0001_RemotePeerInitial"),
    ]

    operations = [
        migrations.RunPython(makeNewPeer),
    ]