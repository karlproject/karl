from appendonly import Accumulator

from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IProfile
from karl.utils import find_catalog

def evolve(site):
    """Convert profile's '_pending_alerts' to an Accumulator.
    """
    catalog = find_catalog(site)
    search = ICatalogSearch(site)
    count, docids, resolver = search(
        interfaces={'query': [IProfile]})
    for docid in docids:
        doc = resolver(docid)
        alerts = doc._pending_alerts
        if not isinstance(alerts, Accumulator):
            doc._pending_alerts = Accumulator(list(alerts))
