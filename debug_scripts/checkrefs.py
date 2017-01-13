"""
Checks a ZODB database for referential integrity. Will print the zoids for any
references found to non-existant objects.
"""

from collections import deque

from ZODB.POSException import POSKeyError
from ZODB.serialize import referencesf
from ZODB.utils import p64, u64

def main():
    storage = root._p_jar._storage
    connection = getattr(storage, '_load_conn', None)
    if connection is not None:
        check_relstorage(connection)
    else:
        check_any_storage(storage)


def check_relstorage(connection):
    curr_objs = connection.cursor()
    cursor = connection.cursor()
    curr_objs.execute('select zoid, tid from current_object')
    for zoid, tid in curr_objs:
        cursor.execute('select state from object_state where zoid=%s and tid=%s',
                       (zoid, tid))
        state = cursor.fetchone()[0]
        if state is None:
            continue  # How would an object have a null state?
        for ref_zoid in referencesf(state):
            ref_zoid = u64(ref_zoid)
            cursor.execute('select tid from current_object where zoid=%s',
                           (ref_zoid,))
            if cursor.rowcount == 0:
                print "Bad reference found", ref_zoid


def check_any_storage(storage):
    checked = set()
    to_check = deque([p64(0)])

    while to_check:
        check_oid = to_check.popleft()
        checked.add(check_oid)
        try:
            state, tid = storage.load(check_oid)
        except POSKeyError:
            print "Bad reference found", u64(check_oid)

        for reference in referencesf(state):
            if reference not in checked:
                to_check.append(reference)


main()