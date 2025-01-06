from django.db import transaction

def set_transaction_metadata(key, value):
    """Stores arbitrary data in a special field on the connection associated with this transaction.
    
    Effectively allows for the storage of temporary data during a single transaction.
    
    Cleans itself up once the commit has completed."""
    connection = transaction.get_connection()
    if not hasattr(connection, '_transaction_metadata'):
        connection._transaction_metadata = {}
    connection._transaction_metadata[key] = value

    def on_commit():
        if hasattr(connection, '_transaction_metadata'):
            del connection._transaction_metadata
    transaction.on_commit(on_commit)

def get_transaction_metadata(key, default=None):
    """
    Retrieves arbitrary data in a special field on the connection associated with this transaction.

    If the key is not set, return default, default is also set in the metadata.

    Effectively allows for the storage of temporary data during a single transaction.

    Cleans itself up once the commit has completed. 
    """
    connection = transaction.get_connection()
    if hasattr(connection, '_transaction_metadata'):
        return connection._transaction_metadata.get(key, default)
    else:
        set_transaction_metadata(key, default)
    return default