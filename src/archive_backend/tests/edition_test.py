import os
from django import setup

from archive_backend.models.remote_peer import RemotePeer
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
setup()

from django.test import TestCase

from archive_backend.models import Edition
from django.db import IntegrityError
from archive_backend.models import AbstractDocument, Language, Author, GenerationConfig, Edition

class EditionIntegrityTest(TestCase):
    def setUp(self):
        self.document = AbstractDocument.objects.create(fallback_name="Test Abstract Document")
        self.language = Language.objects.create(english_name="English", endonym="English", iso_639_code="en")
        self.generation_config = GenerationConfig.objects.create(name="Test Config")
        self.parent_edition = Edition.objects.create(
            edition_of=self.document,
            language=self.language,
            title="Parent Edition",
            description="Description"
        )

    def test_edition_without_generation_config_and_parent(self):
        edition = Edition.objects.create(
            edition_of=self.document,
            language=self.language,
            title="Edition without config and parent",
            description="Description"
        )
        self.assertIsNone(edition.generation_config)
        self.assertIsNone(edition.actively_generated_from)

    def test_edition_with_generation_config_and_parent(self):
        edition = Edition.objects.create(
            edition_of=self.document,
            language=self.language,
            title="Edition with config and parent",
            description="Description",
            generation_config=self.generation_config,
            actively_generated_from=self.parent_edition
        )
        self.assertIsNotNone(edition.generation_config)
        self.assertIsNotNone(edition.actively_generated_from)

    def test_edition_with_generation_config_and_parent(self):
        other_remote = RemotePeer.objects.create(site_name="Other Remote", site_adress="http://other.remote")
        with self.assertRaises(IntegrityError):
            Edition.objects.create(
                from_remote=other_remote,
                edition_of=self.document,
                language=self.language,
                title="Edition with config and parent",
                description="Description",
                generation_config=self.generation_config,
                actively_generated_from=self.parent_edition
            )

    def test_edition_with_generation_config_without_parent(self):
        with self.assertRaises(IntegrityError):
            Edition.objects.create(
                edition_of=self.document,
                language=self.language,
                title="Edition with config without parent",
                description="Description",
                generation_config=self.generation_config
            )

    def test_edition_with_parent_without_generation_config(self):
        with self.assertRaises(IntegrityError):
            Edition.objects.create(
                edition_of=self.document,
                language=self.language,
                title="Edition with parent without config",
                description="Description",
                actively_generated_from=self.parent_edition
            )
