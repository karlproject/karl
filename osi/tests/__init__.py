# shim to atone for usage of zope.testing.cleanUp in the test suite
import zope.testing.cleanup
from pyramid.testing import setUp
zope.testing.cleanup.addCleanUp(setUp)
