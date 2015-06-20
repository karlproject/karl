
"""This tween logs a profile trace whenever it sees a __profile__ query param.
"""

import cProfile
import pstats
import StringIO
import logging


log = logging.getLogger(__name__)


def includeme(config):
    config.add_tween('karl.underprofile.make_tween')


def make_tween(handler, registry):

    def tween(request):
        if '__profile__' not in request.params:
            return handler(request)

        pr = cProfile.Profile()
        pr.enable()
        try:
            return handler(request)
        finally:
            pr.disable()
            s = StringIO.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats('cumtime')
            ps.print_stats(100)  # Limit to 100 lines
            log.warning("Profile of %s:\n%s", request.url, s.getvalue())

    return tween
