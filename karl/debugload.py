
"""This tween shows what KARL is loading from ZODB.

If a __debugload__ query parameter is present in the request, this tween
deactivates all the ZODB objects it can, runs the request, and logs stats
about the kind of objects that were loaded.
"""

from pyramid.events import ContextFound
from pyramid.location import lineage
import collections
import logging


log = logging.getLogger(__name__)


def includeme(config):
    config.add_tween('karl.debugload.make_tween')
    config.add_subscriber(on_context_found, ContextFound)


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
                log_stats(conn, request)
            else:
                log.warning(
                    "Unable to log stats for %s ; the request context "
                    "may not have a ZODB connection", request.url)

    return tween


def on_context_found(event):
    """If debugload is enabled for this request, prepare to measure it."""
    request = event.request
    d = getattr(request, '_debugload_dict', None)
    if d is not None:
        conn = None
        for context in lineage(request.context):
            conn = getattr(context, '_p_jar', None)
            if conn is not None:
                for oid, obj in conn._cache.items():
                    changed = obj._p_changed
                    if changed is not None and not changed:
                        obj._p_deactivate()
                d['conn'] = conn
                break


def log_stats(conn, request):
    """Log stats about what objects were loaded."""
    counts = collections.defaultdict(int)  # {type(obj): count}
    total = 0
    for oid, obj in conn._cache.items():
        total += 1
        t = type(obj)
        if obj._p_changed is not None:
            counts[t] += 1

    lines = []
    stats = [(c1, t1) for (t1, c1) in counts.items()]
    stats.sort(reverse=True)
    for c, t in stats:
        lines.append('%8d %s' % (c, t))

    log.warning(
        "%s ZODB objects loaded by %s:\n%s",
        total, request.url, '\n'.join(lines))
