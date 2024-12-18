from typing import override
from django.test import TestCase
from unittest import mock

from archive_backend.utils.small import HttpUtil


class AlwaysErrorHttpUtilMock(HttpUtil):
    @override
    def get_json_from_remote(self, url):
        raise "Mock for getting json data not implemented for this test"
    
    @override
    def ping_url(self, url):
        raise "Mock for pinging url not implemented for this test"

class ParentTestcase(TestCase):
    def setUp(self):
        patcher3 = mock.patch('archive_backend.utils.HttpUtil', new=AlwaysErrorHttpUtilMock, autospec=True)
        patcher3.start()
        self.addCleanup(patcher3.stop)