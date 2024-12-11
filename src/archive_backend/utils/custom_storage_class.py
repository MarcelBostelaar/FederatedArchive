from django.core.files.storage import FileSystemStorage
import os

class OverwriteStorage(FileSystemStorage):
    """Standard django filesystem storage class, but overwrites files with the 
    same name instead of making new versions with random alternative name modifications.

    Cleans up empty directories after deleting files.

    Neccecary because using default file system and setting it to ALLOW_OVERWRITE = True
    results in the file being overwritten in place (not replaced), corrupting the file.
    
    From https://gist.github.com/fabiomontefuscolo/1584462?permalink_comment_id=4035342#gistcomment-4035342"""
    
    def get_available_name(self, name, max_length=None):
        self.delete(name)
        return super().get_available_name(name, max_length)
    
    def clean_empty_directories(self, name):
        # Get the directory name
        parent_dir = os.path.abspath(os.path.join(name, os.pardir))
        
        # Check if the parent directory is empty and delete it if it is
        if os.path.isdir(parent_dir) and not os.listdir(parent_dir):
            os.rmdir(parent_dir)
            return self.clean_empty_directories(parent_dir)
        return

    def delete(self, name):
        super().delete(name)
        self.clean_empty_directories(name)
