import sys
import transaction
from zope.component import queryUtility
from zope.interface import alsoProvides

from repoze.bfg.traversal import model_path
from repoze.bfg import testing
from repoze.workflow import get_workflow
from repoze.lemonade.content import create_content

from karl.bootstrap.interfaces import IInitialData
from karl.bootstrap.data import DefaultInitialData
from karl.models.interfaces import IIntranets
from karl.content.views.intranets import AddIntranetFormController
from karl.models.site import Site
from karl.models.interfaces import IProfile
from karl.views.community import AddCommunityFormController

def populate(root, do_transaction_begin=True):
    if do_transaction_begin:
        transaction.begin()

    data = queryUtility(IInitialData, default=DefaultInitialData())
    site = root['site'] = Site()
    site.__acl__ = data.site_acl

    # If a catalog database exists and does not already contain a catalog,
    # put the site-wide catalog in the catalog database.
    main_conn = root._p_jar
    try:
        catalog_conn = main_conn.get_connection('catalog')
    except KeyError:
        # No catalog connection defined.  Put the catalog in the
        # main database.
        pass
    else:
        catalog_root = catalog_conn.root()
        if 'catalog' not in catalog_root:
            catalog_root['catalog'] = site.catalog
            catalog_conn.add(site.catalog)
            main_conn.add(site)

    # the ZODB root isn't a Folder, so it doesn't send events that
    # would cause the root Site to be indexed
    docid = site.catalog.document_map.add(model_path(site))
    site.catalog.index_doc(docid, site)
    site.docid = docid

    # the staff_acl is the ACL used as a basis for "public" resources
    site.staff_acl = data.staff_acl

    site['profiles'].__acl__ = data.profiles_acl

    site.moderator_principals = data.moderator_principals
    site.member_principals = data.member_principals
    site.guest_principals = data.guest_principals

    profiles = site['profiles']

    users = site.users

    for login, firstname, lastname, email, groups in data.users_and_groups:
        users.add(login, login, login, groups)
        profile = profiles[login] = create_content(IProfile,
                                                   firstname=firstname,
                                                   lastname=lastname,
                                                   email=email,
                                                  )
        workflow = get_workflow(IProfile, 'security', profiles)
        if workflow is not None:
            workflow.initialize(profile)

    # tool factory wants a dummy request
    COMMUNIITY_INCLUDED_TOOLS = data.community_tools
    class FauxPost(dict):
        def getall(self, key):
            return self.get(key, ())
    request = testing.DummyRequest()
    request.environ['repoze.who.identity'] = {
            'repoze.who.userid': data.admin_user,
            'groups': data.admin_groups,
           }

    # Create a Default community
    request.POST = FauxPost(request.POST)
    converted = {}
    converted['title'] = 'default'
    converted['description'] = 'Created by startup script'
    converted['text'] = '<p>Default <em>values</em> in here.</p>'
    converted['security_state'] = 'public'
    converted['tags'] = ''
    converted['tools'] = COMMUNIITY_INCLUDED_TOOLS

    communities = site['communities']
    add_community = AddCommunityFormController(communities, request)
    add_community.handle_submit(converted)
    communities['default'].title = 'Default Community'

    # Import office data, if there is any
    office_data = data.office_data
    if office_data is not None:
        INTRANET_INCLUDED_TOOLS = data.intranet_tools
        converted = {}
        converted['title'] = 'offices'
        converted['description'] = 'Intranet'
        converted['text'] = ''
        converted['security_state'] = 'public'
        converted['tags'] = ''
        converted['tools'] = INTRANET_INCLUDED_TOOLS
        add_community = AddCommunityFormController(site, request)
        add_community.handle_submit(converted)
        offices = site['offices']
        offices.title = office_data.title

        offices.__acl__ = office_data.offices_acl
        offices.feature = office_data.feature
        alsoProvides(offices, IIntranets)
        #_reindex(offices)

        from karl.content.views.forum import AddForumFormController
        for office in office_data.offices:
            converted = {}
            converted['name'] = office['id']
            converted['title'] = office['id']
            converted['address'] = office['address']
            converted['city'] = office['city']
            converted['state'] = office['state']
            converted['country'] = office['country']
            converted['zipcode'] = office['zipcode']
            converted['telephone'] = office['telephone']
            converted['navigation'] = office['navmenu']
            converted['middle_portlets'] = '\n'.join(office['middle_portlets'])
            converted['right_portlets'] = '\n'.join(office['right_portlets'])
            add_intranet_view = AddIntranetFormController(offices, request)
            add_intranet_view.handle_submit(converted)
            new_office = offices[office['id']]
            new_office.title = office['title']
            # Now add some forums
            for forum in office['forums']:
                converted = {}
                converted['title'] = forum['id']
                converted['description'] = 'No description'
                r = testing.DummyRequest()
                c = AddForumFormController(new_office['forums'], r)
                c.handle_submit(converted)
                new_forum = new_office['forums'][forum['id']]
                new_forum.title = forum['title']

        # Setup reference manuals, network news, network events folders
        from karl.content.views.files import AddFolderFormController
        from karl.content.views.files import advanced_folder_view
        markers = data.folder_markers
        for marker in markers:
            converted = {'title':marker[0], 'security_state':'inherits',
                         'tags':[]}
            if marker[3] is None:
                target = offices
            else:
                target = offices[marker[3]]
            r = testing.DummyRequest()
            c = AddFolderFormController(target, r)
            c.handle_submit(converted)
            target[marker[0]].title = marker[1]
            request.POST.clear()
            request.POST['form.submitted'] = True
            request.POST['marker'] = marker[2]
            advanced_folder_view(target[marker[0]], request)

        # Now the terms and conditions, and privacy statement
        from karl.content.views.page import add_page_view
        for page in office_data.pages:
            request.POST.clear()
            request.POST['form.submitted'] = True
            request.POST['title'] = page[0]
            request.POST['text'] = page[2]
            add_page_view(offices['files'], request)
            offices['files'][page[0]].title = page[1]


    # Set up default feeds from snapshots.
    #import os
    #import feedparser
    #from karl.models.interfaces import IFeedsContainer
    #from karl.models.interfaces import IFeed
    #feeds_container = create_content(IFeedsContainer)
    #site['feeds'] = feeds_container
    #snapshot_dir = os.path.join(os.path.dirname(data.__file__), 'feedsnapshots')
    #for name in os.listdir(snapshot_dir):
        #feed_name, ext = os.path.splitext(name)
        #if ext != '.xml':
            #continue
        #path = os.path.abspath(os.path.join(snapshot_dir, name))
        #parser = feedparser.parse(path)
        #feed = create_content(IFeed, feed_name)
        #feed.update(parser)
        #feeds_container[feed_name] = feed

    bootstrap_evolution(root)

def bootstrap_evolution(root):
    from zope.component import getUtilitiesFor
    from repoze.evolution import IEvolutionManager
    for pkg_name, factory in getUtilitiesFor(IEvolutionManager):
        __import__(pkg_name)
        package = sys.modules[pkg_name]
        manager = factory(root, pkg_name, package.VERSION)
        # when we do start_over, we unconditionally set the database's
        # version number to the current code number
        manager._set_db_version(package.VERSION)
