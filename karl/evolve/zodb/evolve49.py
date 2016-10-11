# Set initial password expiration date for profiles where it is unset
from datetime import datetime
from datetime import timedelta
from random import randint

from karl.utils import find_catalog
from karl.utils import find_profiles


def evolve(context):
    today = datetime.utcnow()
    catalog = find_catalog(context)
    profiles = find_profiles(context)
    for profile in profiles.values():
        days = 180
        expiration_date = today + timedelta(days=days)
        if profile.password_expiration_date is None:
            print('Setting profile %s password expiration date to "%s"' %
                  (profile.__name__, expiration_date))
            profile.password_expiration_date = expiration_date
