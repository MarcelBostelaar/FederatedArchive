# your_app/management/commands/generate_dummy_data.py
import random
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from faker import Faker

from archive_backend.models import *

class Command(BaseCommand):
    help = 'Generates dummy data for testing'

    def handle(self, *args, **kwargs):
        fake = Faker()
        for _ in range(4):
            try:
                FileFormat.objects.create(
                    format=fake.file_extension()
                )
            except IntegrityError as e: 
                print('Unique constraint fail on file format dummy')
        print("Finished generating FileFormat")


        for _ in range(4):
            try:
                Language.objects.create(
                    iso_639_code=fake.language_code(),
                    english_name=fake.language_name(),
                    endonym=fake.word(),
                    child_language_of=None
                )
              
            except IntegrityError as e: 
                print('Unique constraint fail on language dummy')
        print("Finished generating Language")
          
        

        for _ in range(4):
            Author.objects.create(
                fallback_name=fake.name(),
                birthday=fake.date_of_birth()
            )
        print("Finished generating Author")

        for _ in range(10):
            AuthorDescriptionTranslation.objects.create(
                describes=random.choice(Author.objects.all()),
                language=random.choice(Language.objects.all()),
                translation=fake.name(),
                description=fake.text()
            )
        print("Finished generating AuthorDescriptionTranslation")

        for _ in range(4):
            x = AbstractDocument.objects.create(
                original_publication_date=fake.date_this_century(),
                fallback_name=fake.word()
            )
            x
            x.authors.set(random.choices(Author.objects.all(), k=random.randint(1, 3)))
        print("Finished generating AbstractDocument")

        for _ in range(4):
            AbstractDocumentDescriptionTranslation.objects.create(
                describes=random.choice(AbstractDocument.objects.all()),
                language=random.choice(Language.objects.all()),
                translation=fake.word(),
                description=fake.text()
            )
        print("Finished generating AbstractDocumentDescriptionTranslation")

        for _ in range(4):
            Edition.objects.create(
                edition_of = random.choice(AbstractDocument.objects.all()),
                publication_date = fake.date_this_century(),
                language = random.choice(Language.objects.all()),
                title = fake.word(),
                description = fake.text()
            )
        print("Finished generating Edition")
            

        for _ in range(4):
            Revision.objects.create(
                belongs_to=random.choice(Edition.objects.all()),
                date=fake.date_this_century(),
                entry_file= None,
                status = RevisionStatus.UNFINISHED
            )
        print("Finished generating Revision")
            
        self.stdout.write(self.style.SUCCESS('Successfully generated dummy data!'))
