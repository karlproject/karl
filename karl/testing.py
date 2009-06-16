# Copyright (C) 2008-2009 Open Society Institute
#               Thomas Moroz: tmoroz@sorosny.org
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License Version 2 as published
# by the Free Software Foundation.  You may not use, modify or distribute
# this program under any other version of the GNU General Public License.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from cStringIO import StringIO

from zope.interface import implements
from zope.interface import Interface

from repoze.bfg.testing import DummyModel
from repoze.bfg.testing import registerAdapter
from repoze.bfg.testing import registerDummyRenderer
from repoze.bfg.testing import registerUtility

from karl.models.interfaces import ICommunity
from karl.models.interfaces import IProfile

dummy_vocabularies = {
    'departments': [
        {'id': u'department1', 'title': u'Department 1',},
        ],

    'countries': [
        ('DU', 'Durham'),
        ('CH', 'Chapel Hill'),
        ],
    }


class DummyCatalog:
    def __init__(self, *maps):
        self.document_map = DummyDocumentMap(*maps)
        self.queries = []
        self.indexed = []
        self.unindexed = []
        self.reindexed = []
        self.maps = list(maps)

    def index_doc(self, docid, object):
        self.indexed.append(object)

    def unindex_doc(self, docid):
        self.unindexed.append(docid)

    def reindex_doc(self, docid, object):
        self.reindexed.append(object)

    def search(self, **kw):
        self.queries.append(kw)
        try:
            result = self.maps.pop(0)
        except IndexError:
            return 0, ()
        result = sorted(result.keys())
        return len(result), result

class DummyDocumentMap:
    def __init__(self, *maps):
        self.added = []
        self.removed = []
        self.maps = list(maps)

    def add(self, path, docid=None):
        self.added.append((docid, path))
        return 1

    def docid_for_address(self, path):
        for docid, spath in self.added:
            if path == spath:
                return docid

        for map in self.maps:
            for docid, spath in map.items():
                if path == spath:
                    return docid

    def address_for_docid(self, docid):
        for sdocid, path in self.added:
            if sdocid == docid:
                return path

        for map in self.maps:
            for sdocid, path in map.items():
                if sdocid == docid:
                    return path

    def remove_docid(self, docid):
        self.removed.append(docid)
        
class DummyProfile(DummyModel):
    implements(IProfile)
    
    title = 'title'
    firstname = 'firstname'
    lastname = 'lastname'
    position = 'position'
    organization = 'organization'
    phone = 'phone'
    extension = 'extension'
    department = 'department1'
    location = 'location'
    
    def __init__(self, *args, **kw):
        DummyModel.__init__(self)
        for item in kw.items():
            setattr(self, item[0], item[1])
        self._alert_prefs = {}
        self._pending_alerts = []
        
    @property
    def email(self):
        return "%s@x.org" % self.__name__

    def get_photo(self):
        return None

    def get_alerts_preference(self, community_name):
        return self._alert_prefs.get(community_name, 
                                     IProfile.ALERT_IMMEDIATELY)
    
    def set_alerts_preference(self, community_name, preference):
        if preference not in (
            IProfile.ALERT_IMMEDIATELY,
            IProfile.ALERT_DIGEST,
            IProfile.ALERT_NEVER):
            raise ValueError("Invalid preference.")
        
        self._alert_prefs[community_name] = preference

class DummyRoot(DummyModel):
    def __init__(self):
        DummyModel.__init__(self)
        self[u'profiles'] = DummyModel()
        dummies = [
            (u'dummy1', u'Dummy One'),
            (u'dummy2', u'Dummy Two'),
            (u'dummy3', u'Dummy Three'),
            ]
        for dummy in dummies:
            self[u'profiles'][0] = DummyModel(title=dummy[1])
        self[u'communities'] = DummyModel()
        self.system_name = u"karl3test"
        self.system_email_domain = u"karl3.example.com"
        self.vocabularies = dummy_vocabularies
        
class DummyAdapter:
    def __init__(self, context, request):
        self.context = context
        self.request = request

class DummyCommunity(DummyModel):
    implements(ICommunity)
    title = u'Dummy Communit\xe0'
    description = u'Dummy Description'

    def __init__(self):
        DummyModel.__init__(self)
        root = DummyRoot()
        root["communities"]["community"] = self

class DummyMailer(list):
    class DummyMessage(object):
        def __init__(self, mfrom, mto, msg):
            self.mfrom = mfrom
            self.mto = mto
            self.msg = msg
            assert isinstance(msg, str)
            
    def send(self, mfrom, mto, msg):
        self.append(self.DummyMessage(mfrom, mto, msg))

class DummyUsers:
    def __init__(self, community=None):
        self.removed_users = []
        self.removed_groups = []
        self.added_groups = []
        self.community = community
        self._by_id = {}
        self._by_login = {}

    def add(self, userid, login, password, groups, encrypted=False):
        self.added = (userid, login, password, groups)
        userinfo = {
            "id": userid,
            "login": login,
            "password": password,
            "groups": groups,
            }
        self._by_login[login] = userinfo
        self._by_id[userid] = userinfo

        if (self.community is not None and 
            hasattr(self.community, "moderators_group_name") and 
            hasattr(self.community, "members_group_name")):
            for group_name in groups:
                if group_name == self.community.moderators_group_name:
                    self.community.moderator_names.add(userid)
                elif group_name == self.community.members_group_name:
                    self.community.member_names.add(userid)

    def remove(self, userid):
        self.removed_users.append(userid)

    def add_group(self, userid, group_name):
        self.added_groups.append((userid, group_name))
        if (self.community is not None and 
            hasattr(self.community, "moderators_group_name") and 
            hasattr(self.community, "members_group_name")):
            if group_name == self.community.moderators_group_name:
                self.community.moderator_names.add(userid)
            elif group_name == self.community.members_group_name:
                self.community.member_names.add(userid)

    def remove_group(self, userid, group_name):
        self.removed_groups.append((userid, group_name))

        if (self.community is not None and 
            hasattr(self.community, "moderators_group_name") and 
            hasattr(self.community, "members_group_name")):
            if group_name == self.community.moderators_group_name:
                self.community.moderator_names.remove(userid)
            elif group_name == self.community.members_group_name:
                if userid in self.community.member_names:
                    self.community.member_names.remove(userid)

    def get_by_id(self, userid):
        if self._by_id.has_key(userid):
            return self._by_id[userid]
        return None

    def get_by_login(self, login):
        if self._by_login.has_key(login):
            return self._by_login[login]
        return None

    def change_password(self, userid, password):
        from repoze.who.plugins.zodb.users import get_sha_password
        self._by_id[userid]["password"] = get_sha_password(password)
    
class DummyUpload(object):
    """Simulates an HTTP upload.  Suitable for assigning as the value to 
    to a dummy request form parameter.
    """
    def __init__(self, filename="test.txt",
                       mimetype="text/plain",
                       data="This is a test."):
        self.filename = filename
        self.type = mimetype
        self.data = data
        self.file = StringIO(data)

class DummySearchAdapter:
    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def __call__(self, **kw):
        if kw.get('texts') == 'the':
            # simulate a text index parse exception
            from zope.index.text.parsetree import ParseError
            raise ParseError("Query contains only common words: 'the'")
        return 0, [], None

class DummyTagQuery(DummyAdapter):
    tagswithcounts = []
    docid = 'ABCDEF01'

class DummyFolderAddables(DummyAdapter):
    def __init__(self, context, request):
        pass

    def __call__(self):
        return [
            ('Add Folder', 'add_folder.html'),
            ('Add File', 'add_file.html'),
            ]

class DummyFolderCustomizer(DummyAdapter):
    markers = []

class DummyShowSendalert(DummyAdapter):
    show_sendalert = True

class DummyLayoutProvider(DummyAdapter):
    template_fn = 'templates/community_layout.fn'

    def __call__(self, default):
        renderer = registerDummyRenderer(self.template_fn)
        return renderer

class DummyOrdering:
    _items = []

    def sync(self, entries):
        pass

    def moveUp(self, name):
        pass

    def moveDown(self, name):
        pass

    def add(self, name):
        pass

    def remove(self, name):
        pass

    def items(self):
        return []

    def previous_name(self, name):
        return u'previous1'

    def next_name(self, name):
        return u'next1'

class DummySecurityWorkflow:
    def __init__(self, context):
        self.context = context

    def setInitialState(self, **kw):
        self.context.initial_state = kw.copy()

    def updateState(self, **kw):
        if kw.get('sharing') in ('true', True):
            self.context.transition_id = 'private'
        elif kw.get('sharing') in ('false', False):
            self.context.transition_id = 'public'

    def getStateMap(self):
        return {}

    def execute(self, transition_id):
        self.context.transition_id = transition_id

def registerLayoutProvider():
    from karl.views.interfaces import ILayoutProvider
    ad = registerAdapter(DummyLayoutProvider, 
                         (Interface, Interface),
                         ILayoutProvider)

def registerTagbox():
    from karl.models.interfaces import ITagQuery
    registerAdapter(DummyTagQuery, (Interface, Interface),
                    ITagQuery)
    
def registerAddables():
    from karl.views.interfaces import IFolderAddables
    registerAdapter(DummyFolderAddables, (Interface, Interface),
                    IFolderAddables)

def registerKarlDates():
    d1 = 'Wednesday, January 28, 2009 08:32 AM'
    def dummy(date, flavor):
        return d1
    from karl.utilities.interfaces import IKarlDates
    registerUtility(dummy, IKarlDates)

def registerCatalogSearch():
    from karl.models.interfaces import ICatalogSearch
    registerAdapter(DummySearchAdapter, (Interface, Interface),
                    ICatalogSearch)
    registerAdapter(DummySearchAdapter, (Interface,),
                    ICatalogSearch)
    
def registerSecurityWorkflow():
    from karl.security.interfaces import ISecurityWorkflow
    registerAdapter(DummySecurityWorkflow, (Interface,),
                    ISecurityWorkflow)
