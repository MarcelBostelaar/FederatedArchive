import os
from django import setup
from django.test import TestCase
from unittest import mock

from archive_backend import utils
from archive_backend.models.remote_peer import RemotePeer
from archive_backend.tests.parent_case import ParentTestcase


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
setup()

import django

from archive_backend.models import Author
class GeneralApiTest(ParentTestcase):
    def setUp(self):
        super().setUp()
        RemotePeer.objects.create(site_name="test_peer", site_adress="http://test_peer.com")
        # self.http_util_patcher = mock.patch('archive_backend.utils.HttpUtil', new=MockHttpUtil)
        # self.http_util_patcher.start()

    def tearDown(self):
        self.http_util_patcher.stop()

    def test_authors_creation(self):
        pass