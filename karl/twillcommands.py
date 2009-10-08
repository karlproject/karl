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

"""Extend Twill with commands unique to KARL tests

"""


__all__ = ['login',
           'logout',
           'set_random_word', 
           'make_intranets',
           'make_community',
           'remove_community',
           'make_forum',
           'remove_forum',
           'timeit',
           'catalog_find',
           'catalog_notfind',
           'add_members',
           'livesearch_find',
           'livesearch_notfind',
           'add_tag',
           'xpath'
           ]

DEBUG=True
from twill import namespaces, commands
import os
import random
import urllib
from twill import get_browser
from time import time
from twill.errors import TwillAssertionError
from lxml.html import document_fromstring
from simplejson import loads
from urlparse import urljoin

# Globally set the a variable that gives us the name of 
# the test.  Use the current working directory to provide 
# the name.  We use this primarily to make a community for 
# the purpose of an individual test.
test_name = os.path.basename(os.getcwd())

def dump(msg):
    """Simplify the process of writing a message to the console"""

    if DEBUG:
        print>>commands.OUT, msg

def login(username):
    """Find user for given username and make the browser logged in"""

    global_dict, local_dict = namespaces.get_twill_glocals()

    # Set a globabl Twill variable to let Twill scripts now the name
    # of the test, e.g. the directory, as well as community name.
    #global_dict['test_name'] = test_name
    #global_dict['community_name'] = test_name + "-testcase"
    global_dict['cwd'] = os.getcwd()

    hn = global_dict['localhost_url']

    # First logout
    logout()

    # Do a login
    au = global_dict['%s_user' % username]

    # Echo to screen
    dump("Logging into %s as %s" % (hn, au))
    
    # Continue
    ap = global_dict['%s_password' % username]
    commands.go(hn + '/login.html')
    commands.fv("formLogin", "login", au)
    commands.fv("formLogin", "password", ap)
    commands.submit()

    # Make sure the login succeeded
    commands.find("My Profile")

def logout():
    """Visit the logout screen"""

    global_dict, local_dict = namespaces.get_twill_glocals()

    # Visit the logout URL
    hn = global_dict['localhost_url']
    commands.go(hn + '/logout')

    # Make sure the login succeeded
    commands.find("Remember me")

def set_random_word(varname):
    """Create a random word based by adding an int to varname """

    global_dict, local_dict = namespaces.get_twill_glocals()

    randint = str(random.randint(100000, 999999))
    global_dict[varname] = varname + randint

def make_intranets(intranets_name):
    """ Make the offices root hierarchy, deleting if it exists"""

    global_dict, local_dict = namespaces.get_twill_glocals()

    global_dict['intranets_name'] = intranets_name

    # Check to see if we have that community, if so, delete it.
    commands.go('/' + intranets_name)
    br = get_browser()
    status = br.get_code()
    if status != 404:
        # The community shouldn't exist, and so we should get 404
        # looking for it.  If no 404, then it exists and we should
        # delete it.
        url = "/%s/delete.html?confirm=1" % intranets_name
        commands.go(url)

    # Now, make the community and make sure it exists
    commands.go("/add_community.html")
    commands.fv("save", "title", intranets_name)
    desc = "Test intranets root created for Twill test case named '%s'"
    commands.fv("save", "description", desc % test_name)
    commands.submit()
    commands.find("Add Existing")
    

def make_community(community_name=test_name, title=None):
    """Make a community, deleting first if the community exists"""

    global_dict, local_dict = namespaces.get_twill_glocals()
    # Append "-testcase" to the community name, so we can spot later
    # which were created by Twill
    if community_name == test_name:
        community_name = global_dict.get('community_name', 
                                         test_name + '-testcase')
        global_dict['test_name'] = test_name
        global_dict['community_name'] = community_name
    community_name = global_dict['community_name']
    # Echo to screen
    dump("Community is %s" % (community_name))

    if title is None:
        title = community_name

    # Check to see if we have that community, if so, delete it.
    commands.go("/communities/" + community_name)
    br = get_browser()
    status = br.get_code()
    if status != 404:
        # The community shouldn't exist, and so we should get 404
        # looking for it.  If no 404, then it exists and we should
        # delete it.
        # Echo to screen
        dump("Deleted old version of Community: %s " % (community_name))
        url = "/communities/%s/delete.html?confirm=1" % community_name
        commands.go(url)
    else:
        dump("Didn't delete old version of Community: %s " % (community_name))
    # Now, make the community and make sure it exists
    commands.go("/communities/add_community.html")
    commands.fv("save", "title", title)
    desc = "Test community created for Twill test case named '%s'"
    commands.fv("save", "description", desc % community_name)
    commands.submit()
    commands.find("Add Existing")

def remove_community(community_name):
    """Remove a community and make sure it is gone"""

    # Normally we don't need to do this, as make_community internally
    # does a delete before adding.

    global_dict, local_dict = namespaces.get_twill_glocals()

    # Go to the community, see if it exists.  If not, log a message.
    # If so, delete it.
    commands.go("/communities/" + community_name)
    br = get_browser()
    status = br.get_code()
    if status != 200:
        msg = "Community %s not returning 200, must exist"
        dump(msg % community_name)
    else:
        url = "/communities/%s/delete.html?confirm=1" % community_name
        commands.go(url)
        commands.title("Communities")

def make_forum(forum_name=test_name, title=None):
    """Make a forum, deleting first if the forum exists"""

    global_dict, local_dict = namespaces.get_twill_glocals()

    # Append "-testcase" to the community name, so we can spot later
    # which were created by Twillif community_name == test_name:
    if forum_name == test_name:
        forum_name = global_dict.get('forum_name', 
                                         test_name + '-forum-testcase')
        global_dict['test_name'] = test_name
        global_dict['forum_name'] = forum_name
    forum_name = global_dict['forum_name']

    # Echo to screen
    dump("Forum is %s" % forum_name)

    if title is None:
        title = forum_name

    # Check to see if we have that community, if so, delete it.
    commands.go("/offices/forums/%s" % (forum_name))
    br = get_browser()
    status = br.get_code()
    if status != 404:
        # The community shouldn't exist, and so we should get 404
        # looking for it.  If no 404, then it exists and we should
        # delete it.
        # Echo to screen
        dump("Deleted old version of Forum: %s " % (forum_name))
        url = "/offices/forums/%s/delete.html?confirm=1" % forum_name
        commands.go(url)
        commands.title("Forums")
    else:
        dump("Didn't delete old version of Forum: %s " % (forum_name))
    # Now, make the community and make sure it exists
    commands.go("/offices/forums/add_forum.html")
    commands.fv("save", "title", title)
    desc = "Test forum created for Twill test case named '%s'"
    commands.fv("save", "description", desc % forum_name)
    commands.submit()
    commands.find("Add Forum Topic")

def remove_forum(forum_name):
    """Remove a community and make sure it is gone"""

    # Normally we don't need to do this, as make_community internally
    # does a delete before adding.

    global_dict, local_dict = namespaces.get_twill_glocals()

    # Go to the forum, see if it exists.  If not, log a message.
    # If so, delete it.
    commands.go("/offices/forums/" + forum_name)
    br = get_browser()
    status = br.get_code()
    if status != 200:
        msg = "Community %s not returning 200, must exist"
        dump(msg % forum_name)
    else:
        url = "/offices/forums/%s/delete.html?confirm=1" % forum_name
        commands.go(url)
        commands.title("Forums")

def timeit(msg):
    """Keep partial and total elapsed times and print to console"""

    # Although performance testing takes some different thought than
    # functional testing, we'd like to have some easy and convenient
    # ways to watch elapsed time.  This command can be sprinkled
    # throughout a test run to show 2 kinds of time:
    #     - Elapsed time since the start of the first "timeit" 
    #     - Elapsed time since the previous "timeit" 
    # Putting a line such as this in your .twill script:
    #     timeit "Some Stinking Message" 
    # ...causes a line like this to be printed to the console: 
    #     Timeit: 0.02323,14.938,Some Stinking Message
    # You could thus run a test, ignoring the functional testing 
    # output, and showing just the timing:
    #     ../runtest.sh | grep Timeit

    global_dict, local_dict = namespaces.get_twill_glocals()

    # Get the first_time and previous_time variables.  If they don't
    # exist, set them.
    first_time = global_dict.get("first_time", False)
    if not first_time:
        global_dict['first_time'] = first_time = time()
    previous_time = global_dict.get("previous_time", False)
    if not previous_time:
        global_dict['previous_time'] = previous_time = first_time

    # Calculate times
    elapsed1 = time() - previous_time
    elapsed2 = time() - first_time

    fmt = "Timeit: %.3f,%.3f,%s"
    dump(fmt % (elapsed1, elapsed2, msg))

    # Reset previous_time
    global_dict['previous_time'] = time()

def livesearch_find(group, term, titleword, notfind=False):
    """See if the term appears in one of the LiveSearch groups"""

    global_dict, local_dict = namespaces.get_twill_glocals()

    # This will navigate us away from the place the Twill script is
    # sitting.  Thus, stash away to the current URL, then navigate
    # back to that URL after searching.
    br = get_browser()
    start_url = br.get_url()

    # We issue a request and get an XML response
    esc_searchterm = urllib.quote(term)
    url = global_dict['localhost_url'] + "/jquery_livesearch?val=" + esc_searchterm
    commands.go(url)
    doc = loads(br.get_html())

    # Grab the correct /response/kind
    kind = ''
    groups = {}
    titles = []
    pre = None
    for result in doc:
        if result['pre'][0:19] == u'<div class="header"':
            # We started a batching group
            pre = result['pre'][20:-6]
            groups[pre] = []

        # We are inside one of the groupings
        title = result['title']
        if titleword in title:
            groups[pre].append(result['title'])

    hasterm = len(groups[group])

    if notfind:
        # Let the _notfind version decide what to do with 
        # the error
        return hasterm

    if not hasterm:
        msg = "LiveSearch does not contain %s in group %s"
        raise TwillAssertionError(msg % (term, group))
    else:
        msg = "LiveSearch contains %s in group %s"
        dump(msg % (term, group))


def livesearch_notfind(group, term, titleword):
    """Just like Twill notfind, but issues a LiveSearch search"""

    hasterm = livesearch_find(group, term, titleword, notfind=True)

    if hasterm:
        msg = "LiveSearch does not contain %s in group %s"
        raise TwillAssertionError(msg % (term, group))
    else:
        msg = "LiveSearch contains %s in group %s"
        dump(msg % (term, group))


def catalog_find(searchterm, urlfrag, notfind=False):
    """Just like Twill find, but issues a searchpage-search search"""

    global_dict, local_dict = namespaces.get_twill_glocals()

    # This will navigate us away from the place the Twill script is
    # sitting.  Thus, stash away to the current URL, then navigate
    # back to that URL after searching.
    br = get_browser()
    start_url = br.get_url()

    esc_searchterm = urllib.quote(searchterm)
    url = "/searchresults.html?body=" + esc_searchterm
    commands.go(url)

    # Now do the test.  With the fragment of the URL that was
    # provided, we can do a double-check, to make sure the
    # searchresults provide that.
    if notfind:
        commands.notfind(urlfrag)
    else:
        commands.find(urlfrag)

    # Finally, send them back to the original URL.
    commands.go(start_url)


def catalog_notfind(searchterm, urlfrag):
    """Just like Twill find, but issues a Xapian search"""

    catalog_find(searchterm, urlfrag, True)

def add_members(community_name, user1, user2=None):
    """Add one and optionally 2 users to a community"""

    global_dict, local_dict = namespaces.get_twill_glocals()

    l_url = global_dict['localhost_url']
    community_url = urljoin(l_url, 'communities/' + community_name)
    add_member_url = community_url + '/members/add_existing.html'
    commands.go(add_member_url)
    commands.find('Add Existing')
    commands.fv('save', 'users', user1)
    commands.submit()
    if user2:
        commands.go(add_member_url)
        commands.find('Add Existing')
        commands.fv('save', 'users', user2)
        commands.submit()        

def add_tag(tagname):
    """ Add a tag to a piece of content.

    o This is an emuatilon of what the AJAX stuff does:  a better test
      would actually use the AJAX somehow (e.g., via Selenium).
    """


    br = get_browser()
    start_url = br.get_url()

    # Make the URL used (inapproriately) for the GET
    current_url = br.get_url().split('?')[0]
    if current_url.endswith('.html'):
        current_url = current_url.rsplit('/', 1)[0]
    if current_url[-1] != '/':
        # Wish urljoin didn't remove the last hop
        current_url += '/'
    tag_url = urljoin(current_url, 'jquery_tag_add?val=%s' % tagname)

    # Go to the tag url, then go back where you were
    commands.go(tag_url)
    commands.go(start_url)


def xpath(expr, result):
    """Given an XPath expression, see if it returns the result"""

    br = get_browser()
    xhtml = br.get_html()
    et = document_fromstring(xhtml)
    xpath_result = str(et.xpath(expr))

    if xpath_result!=result:
        msg = "XPath expression '%s' returned %s instead of %s"
        raise TwillAssertionError(msg % (expr, xpath_result, result))
