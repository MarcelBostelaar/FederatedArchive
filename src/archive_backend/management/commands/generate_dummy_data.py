# your_app/management/commands/generate_dummy_data.py
from io import StringIO
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from faker import Faker

from archive_backend import config
from archive_backend.models import *

class Command(BaseCommand):
    help = 'Generates dummy data for testing'

    def add_arguments(self , parser):
        parser.add_argument('--nojobqueing', action='store_true')

    def handle(self, *args, **kwargs):
        config.do_job_queueing = not kwargs.get('nojobqueing', True)
        fake = Faker()
        for i in range(4):
            try:
                FileFormat.objects.create(
                    format="format" + str(i)
                )
            except IntegrityError as e: 
                print('Unique constraint fail on file format dummy')

        text_file_format = FileFormat.objects.create(
            format="txt"
        )
        print("Finished generating FileFormat")


        for i in range(4):
            try:
                Language.objects.create(
                    iso_639_code=fake.language_code(),
                    english_name="language" + str(i),
                    endonym=fake.word(),
                    child_language_of=None
                )
              
            except IntegrityError as e: 
                print('Unique constraint fail on language dummy')
        print("Finished generating Language")
          
        

        for i in range(4):
            Author.objects.create(
                fallback_name="Author" + str(i),
                birthday=fake.date_of_birth()
            )
        print("Finished generating Author")

        for i in range(4):
            AuthorDescriptionTranslation.objects.create(
                describes=Author.objects.all()[i],
                language=Language.objects.all()[1],
                translation="Translation" + str(i*2),
                description="Description" + str(i*2)
            )
            AuthorDescriptionTranslation.objects.create(
                describes=Author.objects.all()[i],
                language=Language.objects.all()[2],
                translation="Translation" + str(i*2 + 1),
                description="Description" + str(i*2 + 1)
            )
        print("Finished generating AuthorDescriptionTranslation")

        for i in range(4):
            x = AbstractDocument.objects.create(
                original_publication_date=fake.date_this_century(),
                fallback_name="AbstractDocument" + str(i),
            )
        AbstractDocument.objects.first().authors.set(Author.objects.all()[:2])
        print("Finished generating AbstractDocument")

        for i in range(4):
            AbstractDocumentDescriptionTranslation.objects.create(
                describes=AbstractDocument.objects.all()[i],
                language=Language.objects.all()[i],
                translation="Translation" + str(i),
                description=str(i) + ": Lorem ipsum dolor sit amet, consectetur adipiscing elit"
            )
        print("Finished generating AbstractDocumentDescriptionTranslation")


        regular_edition = Edition.objects.create(
            edition_of = AbstractDocument.objects.all()[0],
            publication_date = fake.date_this_century(),
            language = Language.objects.all()[0],
            title = "Regular edition",
            description = "Regular edition description"
        )
        automatically_generated_edition = Edition.objects.create(
            edition_of = AbstractDocument.objects.all()[0],
            publication_date = fake.date_this_century(),
            language = Language.objects.all()[0],
            title = "Generated edition automatic",
            description = "Generated edition description automatic",
            actively_generated_from = regular_edition,
            generation_config = GenerationConfig.objects.create(
                name = "Automatic test config",
                registered_name = "example_generator_plugin.txt_to_caps",
                description = "test config description",
                automatically_regenerate = True,
                config_json = {"test": "config"}
            )
        )
        manually_generated_edition = Edition.objects.create(
            edition_of = AbstractDocument.objects.all()[0],
            publication_date = fake.date_this_century(),
            language = Language.objects.all()[0],
            title = "Generated edition manual",
            description = "Generated edition description manual",
            actively_generated_from = regular_edition,
            generation_config = GenerationConfig.objects.create(
                name = "Manual test config",
                registered_name = "example_generator_plugin.txt_to_caps",
                description = "test config description",
                automatically_regenerate = False,
                config_json = {"test": "config"}
            )
        )
        unpublished_edition = Edition.objects.create(
            edition_of = AbstractDocument.objects.all()[1],
            publication_date = fake.date_this_century(),
            language = Language.objects.all()[1],
            title = "Unpublished edition",
            description = "Unpublished edition description"
        )
        generated_from_unpublished_edition = Edition.objects.create(
            edition_of = AbstractDocument.objects.all()[1],
            publication_date = fake.date_this_century(),
            language = Language.objects.all()[2],
            title = "Unpublished based autogen edition",
            description = "Unpublished based autogen edition description",
            actively_generated_from = unpublished_edition,
            generation_config = GenerationConfig.objects.create(
                name = "Unpublished autogen test config",
                registered_name = "example_generator_plugin.txt_to_caps",
                description = "test config description",
                automatically_regenerate = True,
                config_json = {"test": "config"}
            )
        )

        regular_rev = Revision.objects.create(
            status = RevisionStatus.UNFINISHED,
            belongs_to = regular_edition,
            is_backup = False
        )

        unfinished_rev = Revision.objects.create(
            status = RevisionStatus.UNFINISHED,
            belongs_to = unpublished_edition,
            is_backup = False
        )
        
        file1 = ArchiveFile.objects.create(
            belongs_to = regular_rev,
            file_format = text_file_format,
            file_name = "file1"
        )
        
        file1.file.save("", StringIO("Content of file 1."))
        

        file2 = ArchiveFile.objects.create(
            belongs_to = regular_rev,
            file_format = text_file_format,
            file_name = "file2"
        )
        
        file2.file.save("", StringIO("Content of file 2."))
        
        
        file3 = ArchiveFile.objects.create(
            belongs_to = unfinished_rev,
            file_format = text_file_format,
            file_name = "file3"
        )
        
        file3.file.save("", StringIO("Content of file 3."))
        
        
        file4 = ArchiveFile.objects.create(
            belongs_to = unfinished_rev,
            file_format = text_file_format,
            file_name = "file4"
        )
        
        file4.file.save("", StringIO("Content of file 4."))

        regular_rev.status = RevisionStatus.ONDISKPUBLISHED
        regular_rev.save()
            
        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data!'))
