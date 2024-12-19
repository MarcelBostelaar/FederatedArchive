from typing import override
from django.test import TestCase

from archive_backend import config


class ParentTestcase(TestCase):
    def setUp(self):
        config.unit_testing = True