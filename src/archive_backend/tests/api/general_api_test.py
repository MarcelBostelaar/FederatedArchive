import os
from django import setup
from django.test import TestCase
from unittest import mock

from archive_backend import utils
from archive_backend.tests.parent_case import ParentTestcase


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
setup()

import django

from archive_backend.models import Author

class GeneralApiTest(ParentTestcase):
    def setUp(self):
        super().setUp()
        pass

    def test_authors_creation(self):
        pass