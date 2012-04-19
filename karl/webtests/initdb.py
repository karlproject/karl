"""
Database initialization for WebTests.  This script is run by bin/karlserve debug
and is used to populate the database.

The site root object is available as 'root' in the global namespace.
"""
# DB initialization code goes here

import transaction
transaction.commit()
