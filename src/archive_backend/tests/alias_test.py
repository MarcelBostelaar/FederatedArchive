import os
from django import setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
setup()
from django.test import TestCase

from archive_backend.tests.parent_case import ParentTestcase


import django

from archive_backend.models import Author

class AuthorTestCase(ParentTestcase):
    def setUp(self):
        super().setUp()
        self.author1 = Author.objects.create(fallback_name="Author 1")
        self.author2 = Author.objects.create(fallback_name="Author 2")
        self.author3 = Author.objects.create(fallback_name="Author 3")
        self.author4 = Author.objects.create(fallback_name="Author 4")
        self.author5 = Author.objects.create(fallback_name="Author 5")
        self.author6 = Author.objects.create(fallback_name="Author 6")

    def test_authors_creation(self):
        # Test if the authors are created successfully
        self.assertEqual(Author.objects.count(), 6)

        #New items must have an alias identifier
        self.assertIsNotNone(self.author1.alias_identifier)

        #New identifiers in this test (no aliases) must be unique
        self.assertEqual(len(set([x.alias_identifier for x in Author.objects.all()])), 6)

        self.assertEqual(
            self.author1.alias_origin_end.first().__class__.objects.count(), 6) #6 identities

    def test_alias_creation_direct(self):
        self.author1.addAlias(self.author2)
        self.author1.addAlias(self.author3)

        self.author1.refresh_from_db()
        self.author2.refresh_from_db()
        self.author3.refresh_from_db()
        self.author4.refresh_from_db()
        self.author5.refresh_from_db()
        self.author6.refresh_from_db()

        self.assertEqual(
            self.author1.alias_origin_end.first().__class__.objects.count(),
            6 + 6) #6 identities, 6 aliases (6 sets of 2 items for 3 authors)
        
        firstID = self.author1.alias_identifier
        self.assertEqual(self.author2.alias_identifier, firstID)
        self.assertEqual(self.author3.alias_identifier, firstID)

        #There should be 4 alias identifiers, 3 for 4-6 and 1 for 1-3
        self.assertEqual(len(set([x.alias_identifier for x in Author.objects.all()])), 4)

    def test_alias_creation_indirect(self):
        self.author1.addAlias(self.author2)
        self.author2.addAlias(self.author3)

        self.assertEqual(
            self.author1.alias_origin_end.first().__class__.objects.count(),
            6 + 6) #6 identities, 6 aliases (6 sets of 2 items for 3 authors)
        
    def test_alias_creation_indirect_2(self):
        self.author1.addAlias(self.author2)
        self.author3.addAlias(self.author2)

        self.assertEqual(
            self.author1.alias_origin_end.first().__class__.objects.count(),
            6 + 6) #6 identities, 6 aliases (6 sets of 2 items for 3 authors)
        