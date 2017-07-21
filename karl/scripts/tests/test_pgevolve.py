from newt.db import connection
from newt.db.tests.base import TestCase

class PGEvolveTests(TestCase):

    def test_evolve_from_new_db(self):
        # set up newt:
        connection(self.dsn).close()
        from ..pgevolve import main
        main(self.dsn, True)

