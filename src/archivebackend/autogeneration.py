

import importlib
import os

import requests
from archivebackend.models import Edition, Revision

generationFunctions = {}

revisionFolderName = 'files'
def getRevisionFolderPath(revision):
    return os.path.join(revisionFolderName, str(revision.id))

def generateFiles(sourceEdition, generationConfig, targetRevision):
    latestRevision = getLatestRevision(sourceEdition)
    ensureFilesExistLocally(latestRevision)
    files = latestRevision.files.all()
    plugin = generationFunctions[generationConfig.script_name]
    plugin.generate(files, targetRevision)

def getLatestRevision(sourceEdition):
    # Retrieve the latest revision for the given sourceEdition
    try:
        latest_revision = Revision.objects.filter(belongs_to=sourceEdition).latest('date')
        return latest_revision
    except Revision.DoesNotExist:
        return None
    
def ensureFilesExistLocally(revision):
    # Ensure that files associated with the given revision exist locally
    foldername = os.path.dirname(getRevisionFolderPath(revision))
    os.makedirs(foldername, exist_ok=True)
    for file_record in revision.files.all():
        file_name = file_record.file_format.name  # Replace with your actual file attribute
        file_path = os.path.join(foldername, file_name)

        # If the file doesn't exist locally, download it or perform the necessary actions
        if not os.path.exists(file_path):
            downloadFile(getFileUrl(file_record), file_path)

def getFileUrl(file_record):
    # Implementation for getting the file URL from the file record
    # Assumes a file format attribute in the FileFormat model

    file_format = file_record.file_format

    # Replace 'example.com' with the actual base URL for your files
    base_url = file_record.from_remote.site_adress

    # Replace 'file_extension' with the actual attribute in your FileFormat model
    file_extension = file_format.file_extension

    # Construct the full file URL
    file_url = f"{base_url}{file_record.file_format.name}.{file_extension}"

    return file_url

def downloadFile(file_url, target_path):
    # Implementation for downloading a file from a URL to a local path
    # Uses the requests library for simplicity
    response = requests.get(file_url)

    if response.status_code == 200:
        with open(target_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {file_url} to {target_path}")
    else:
        print(f"Failed to download {file_url} to {target_path}")

class BasePlugin:
    def generate(self, files, targetRevision):
        raise NotImplementedError("Subclasses must implement the generate method. They should take the files, generate new ones, and put them into the database correctly.")

def load_plugins(plugin_folder):
    #TODO reimplemtn once you have brainpower. Must load folders not files. Iterate through all generation configs to see if they exist
    raise NotImplemented()