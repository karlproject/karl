from zope.component import queryUtility
from zope.interface import implements

import pkg_resources

from repoze.bfg.security import Allow
from repoze.bfg.security import Authenticated

from karl.bootstrap.interfaces import IInitialData
from karl.bootstrap.interfaces import IInitialOfficeData

from karl.security.policy import ADMINISTRATOR_PERMS
from karl.security.policy import GUEST_PERMS
from karl.security.policy import MODERATOR_PERMS
from karl.security.policy import NO_INHERIT

_marker = object()

sample_feature = """\
<div>
  <div class="teaser">
    <a href="http://karlproject.org/">
      <img src="/static/images/sample_feature.jpg" />
    </a>
  </div>
  <div class="visualClear"></div>
  <div class="featureLinks">
    <p>
      <a href="http://karlproject.org/newinkarl3.html">What's new in Karl3</a>
    </p>
    <p>
      <a href="http://karlproject.org/isandisnot.html">What Karl is and is not</a>
    </p>
    <p>
      <a href="http://karlproject.org/background.html">Background of Karl</a>
    </p>
    <p>
      <a href="http://dev.karlproject.org/">Developer site</a>
    </p>
  </div>
</div>
"""

navmenu_template = u"""\
<div>
  <div class="menu">
    <h3>About Karl Sample</h3>
    <ul class="nav">
      <li>
        <a href="/about-karlsample" target="" title="">About Karl Sample</a>
      </li>
      <li>
        <a href="/people" target="" title="">Network Directory</a>
      </li>
    </ul>
  </div>

  <div class="menu">
    <h3>About %(org_upper)s</h3>
    <ul class="nav">
      <li>
        <a href="/offices/%(org)s/about/about-%(org)s" target="" title="">About %(org_upper)s</a>
      </li>
      <li>
        <a href="/offices/%(org)s/about/basic-office-info" target="" title="">Basic Office Info</a>
      </li>
    </ul>
  </div>

  <div class="menu">
    <h3>Resources</h3>
    <ul class="nav">
      <li class="submenu">
        <a href="/offices/%(org)s/referencemanuals" target="" title="">Documentation</a>
        <ul class="level2">
          <li>
            <a href="/offices/%(org)s/referencemanuals/manual" target="" title="">Sample manual</a>
          </li>
        </ul>
      </li>
      <li>
        <a href="/offices/%(org)s/forums" target="" title="">Sample Forums</a>
      </li>
    </ul>
  </div>

</div>
"""

class DefaultInitialData(object):
    implements(IInitialData)

    moderator_principals = ['group.KarlModerator']
    member_principals = ['group.KarlStaff']
    guest_principals = []
    community_tools = ('blog', 'wiki', 'calendar', 'files')
    intranet_tools = ('forums', 'intranets', 'files')
    admin_user = 'admin'
    admin_groups = ('group.KarlStaff', 'group.KarlAdmin')

    folder_markers = [
        ('network-news', 'Network News', 'network_news', 'files'),
        ('network-events', 'Network Events', 'network_events', 'files'),
    ]

    site_acl = [
        (Allow, Authenticated, GUEST_PERMS),
        (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS),
        ]

    profiles_acl = [
        (Allow, 'group.KarlUserAdmin', ADMINISTRATOR_PERMS),
        ]

    staff_acl = [
        (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS+MODERATOR_PERMS),
        (Allow, 'group.KarlModerator', MODERATOR_PERMS),
        (Allow, 'group.KarlStaff', GUEST_PERMS)
        ]

    _office_data = _marker
    @property
    def office_data(self):
        if self._office_data is _marker:
            self._office_data = queryUtility(
                IInitialOfficeData, default=DefaultInitialOfficeData())
        return self._office_data

    users_and_groups = [
        ('admin', 'Ad','Min','admin@example.com',
         ('group.KarlAdmin', 'group.KarlUserAdmin', 'group.KarlStaff')),
        ('nyc', 'En', 'Wycee', 'nyc@example.com',
         ('group.KarlStaff',)),
        ('affiliate', 'Aff', 'Illiate', 'affiliate@example.com',
         ('group.KarlAffiliate',)),
        ('staff1','Staff','One','staff1@example.com',
         ('group.KarlStaff',)),
        ('staff2','Staff','Two','staff2@example.com',
         ('group.KarlStaff',)),
        ('staff3','Staff','Three','staff3@example.com',
         ('group.KarlStaff',)),
        ('staff4','Staff','Four','staff4@example.com',
         ('group.KarlStaff',)),
        ('staff5','Staff','Five','staff5@example.com',
         ('group.KarlStaff',)),
        ('staff6','Staff','Six','staff6@example.com',
         ('group.KarlStaff',)),
        ('staff7','Staff','Seven','staff7@example.com',
         ('group.KarlStaff',)),
        ('staff8','Staff','Eight','staff8@example.com',
         ('group.KarlStaff',)),
        ('staff9','Staff','Nine','staff9@example.com',
         ('group.KarlStaff',)),
        ('staff10','Staff','Ten','staff10@example.com',
         ('group.KarlStaff',)),
        ('staff11','Staff','Eleven','staff11@example.com',
         ('group.KarlStaff',)),
        ('staff12','Staff','Twelve','staff12@example.com',
         ('group.KarlStaff',)),
        ('affiliate1','Affiliate','One','affiliate1@example.com',
         ('groups.KarlAffiliate',)),
        ('affiliate2','Affiliate','Two','affiliate2@example.com',
         ('groups.KarlAffiliate',)),
        ('affiliate3','Affiliate','Three','affiliate3@example.com',
         ('groups.KarlAffiliate',)),
        ('affiliate4','Affiliate','Four','affiliate4@example.com',
         ('groups.KarlAffiliate',)),
        ('affiliate5','Affiliate','Five','affiliate5@example.com',
         ('groups.KarlAffiliate',)),
        ('affiliate6','Affiliate','Six','affiliate6@example.com',
         ('groups.KarlAffiliate',)),
        ('affiliate7','Affiliate','Seven','affiliate7@example.com',
         ('groups.KarlAffiliate',)),
        ('affiliate8','Affiliate','Eight','affiliate8@example.com',
         ('groups.KarlAffiliate',)),
        ('affiliate9','Affiliate','Nine','affiliate9@example.com',
         ('groups.KarlAffiliate',)),
        ('affiliate10','Affiliate','Ten','affiliate10@example.com',
         ('groups.KarlAffiliate',)),
        ('affiliate11','Affiliate','Eleven','affiliate11@example.com',
         ('groups.KarlAffiliate',)),
        ('affiliate12','Affiliate','Twelve','affiliate12@example.com',
         ('groups.KarlAffiliate',)),
    ]

sample_forums = [
    {'id': 'karlsample-events', 'title': 'Karl Sample Org Events' },
    {'id': 'karlsample-news', 'title': 'Karl Sample Org News' },
    {'id': 'karlsample-personals', 'title': 'Karl Sample Org Personals' },
    ]

class DefaultInitialOfficeData(object):
    implements(IInitialOfficeData)

    title = 'KarlSample'

    offices = [
        {'id': 'karlsample',
         'title': 'Karl Sample Office',
         'address': '55 Main St, 3rd floor',
         'city': 'Alexandria',
         'state': 'VA',
         'country': 'US',
         'zipcode': '33680',
         'telephone': '01-555-200-38-24/25/26/27',
         'middle_portlets': [],
         'right_portlets': [],
         'forums': sample_forums,
         'navmenu': navmenu_template % {
             'org': 'karlsample',
             'org_upper': 'Karl Sample Org'},
         },
    ]

    offices_acl = [
        (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS),
        (Allow, 'group.KarlStaff', GUEST_PERMS),
        NO_INHERIT,
    ]

    feature = sample_feature

    @property
    def pages(self):
        return [
            ('terms_and_conditions', 'Terms and Conditions',
             pkg_resources.resource_stream(
                 __name__, 'terms_and_conditions.html').read()),
             ('privacy_statement', 'Privacy Statement',
              pkg_resources.resource_stream(
                  __name__, 'privacy_statement.html').read()),
        ]
