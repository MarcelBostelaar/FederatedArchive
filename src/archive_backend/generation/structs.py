import io
import os
import tempfile


class ProcessingFile:
    """Info about a file in processing"""
    def __init__(self, name: str, format: str):
        self.name = name
        self.format = format
        self.path = tempfile.TemporaryFile(delete=False, mode='w+b').name

    def getReadStream(self):
        return open(self.path, 'rb')

    def getTextReadStream(self, encoding = "utf-8"):
        return io.TextIOWrapper(self.getReadStream(), encoding)
    
    def getWriteStream(self):
        return open(self.path, 'wb')
    
    def getTextWriteStream(self, encoding = "utf-8"):
        return io.TextIOWrapper(self.getWriteStream(), encoding)
    
    def __del__(self):
        os.remove(self.path)