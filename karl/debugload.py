
"""This tween shows what KARL is loading from ZODB.

If a __debugload__ query parameter is present in the request, this tween
deactivates all the ZODB objects it can, runs the request, and logs stats
about the kind of objects that were loaded.
"""

from pyramid.events import ContextFound
import collections
import logging


log = logging.getLogger(__name__)


def includeme(config):
    config.add_tween('karl.debugload.make_tween')
    config.add_subscriber(on_context_found, ContextFound)
    config.add_subscriber(on_root_created, RootCreated)


class RootCreated(object):
    """Event broadcast at the creation of the root object for a request."""
    def __init__(self, request, root):
        self.request = request
        self.root = root


def make_tween(handler, registry):
    """Make the debugload tween."""

    def tween(request):
        if '__debugload__' not in request.params:
            return handler(request)

        request._debugload_dict = d = {}
        try:
            return handler(request)
        finally:
            conn = d.get('conn')
            if conn is not None:
                x = d.get('traversal_stats', None)
                if x is not None:
                    traversal_stats, ignore_oids_list = x
                    ignore_oids = set(ignore_oids_list)
                else:
                    traversal_stats = ''
                    ignore_oids = ()

                after_stats, _ = prepare_stats(
                    conn, request, 'after traversal', ignore_oids)

                log.warning(
                    "%s:\n%s\n%s\n",
                    request.url, traversal_stats, after_stats)

            else:
                log.warning("No stats were collected for %s", request.url)

    return tween


def on_root_created(event):
    """If debugload is enabled for this request, prepare to measure it."""
    request = event.request
    d = getattr(request, '_debugload_dict', None)
    if d is not None:
        conn = getattr(event.root, '_p_jar', None)
        if conn is not None:
            for oid, obj in conn._cache.items():
                changed = obj._p_changed
                if changed is not None and not changed:
                    obj._p_deactivate()
            d['conn'] = conn


def on_context_found(event):
    """If debugload is enabled for this request, measure traversal."""
    request = event.request
    d = getattr(request, '_debugload_dict', None)
    if d is not None:
        conn = d.get('conn')
        if conn is not None:
            stats, oids = prepare_stats(conn, request, 'during traversal')
            d['traversal_stats'] = stats, oids


def prepare_stats(conn, request, phase, ignore_oids=()):
    """Gather stats about what objects have been loaded so far."""
    counts = collections.defaultdict(int)  # {type(obj): count}
    oids = []
    for oid, obj in conn._cache.items():
        if oid not in ignore_oids:
            t = type(obj)
            if obj._p_changed is not None:
                oids.append(oid)
                counts[t] += 1

    lines = ['%s ZODB objects loaded %s' % (len(oids), phase)]
    stats = [(c1, t1) for (t1, c1) in counts.items()]
    stats.sort(reverse=True)
    for c, t in stats:
        lines.append('%8d %s' % (c, t))

    return '\n'.join(lines), oids
