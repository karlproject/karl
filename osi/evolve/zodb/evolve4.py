import os
import sys

from karl.peopledir.models.peopledirectory import PeopleDirectory as OSIPeople
from karl.models.peopledirectory import PeopleDirectory as NewPeople

from repoze.lemonade.content import create_content
from karl.models.interfaces import IPeopleDirectory

from karl.scripting import get_default_config
from karl.scripts.peopleconf import run_peopleconf
from osi.sync.gsa_sync import GsaSync

# XXX Update me for production use
GSA_URL = "https://businesscenter.soros.org/gsasync/default.aspx"

def evolve(context):
    """
    Replace OSI's old OSI-specific peopledir implementation with newer,
    universal peopledir.

    NOTE: We have to keep the old peopledir package around at least long
    enough to run this in production.
    """
    if isinstance(context['people'], OSIPeople):
        print "Delete old peopledir"
        del context['people']

        print "Create new peopledir"
        context['people'] = people = create_content(IPeopleDirectory)
        assert isinstance(people, NewPeople)

        print "Perform fresh gsa_sync"
        # Use local copy if available, to save time in testing
        here = os.path.dirname(os.path.dirname(sys.argv[0]))
        local_gsa = os.path.abspath(os.path.join(here, 'gsa_sync.xml'))
        if os.path.exists(local_gsa):
            url = 'file://%s' % local_gsa
            user = password = None
        else:
            url = GSA_URL
            user, password = 'karlgsasync', 'oBaMa2012'
        print "Using url:", url
        GsaSync(context, url, user, password)()

        print "Run peopleconf"
        config = get_default_config()
        run_peopleconf(context, config, force_reindex=True)
