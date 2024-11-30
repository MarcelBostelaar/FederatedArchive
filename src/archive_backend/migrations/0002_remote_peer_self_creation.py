from django.db import migrations

#See migration 1

def makeNewPeer(apps, schema_editor):
    RemotePeer = apps.get_model("archive_backend", "RemotePeer")
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
        ("archive_backend", "0001_remote_peer_initial"),
    ]

    operations = [
        migrations.RunPython(makeNewPeer),
    ]