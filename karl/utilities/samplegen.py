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
"""Add sample users and random sample content.

This is called by a script named "samplegen".
"""

from cgi import escape
from karl.content.views.blog import add_blogentry_view
from karl.content.views.files import add_file_view
from karl.content.views.calendar_events import add_calendarevent_view
from karl.content.views.wiki import add_wikipage_view
from karl.models.interfaces import IProfile
from karl.views.communities import add_community_view
from repoze.bfg import testing
from repoze.bfg.url import model_url
from repoze.lemonade.content import create_content
from repoze.workflow import get_workflow
import datetime
import logging
import lxml.html
import mimetypes
import os
import random
import re

log = logging.getLogger(__name__)

ignore_line_re = re.compile(r'[\[\]*]')
title_word_re = re.compile(r"([A-Z][a-z']+)")

title_word_cache = {}  # filename: set(title_words)

DEFAULT_ENV = {
    'repoze.who.identity': {
        'repoze.who.userid': 'admin',
        'groups': ('group.KarlStaff', 'group.KarlAdmin'),
        },
    }


def get_sample_filename(subdir='sampletext'):
    here = os.path.dirname(__file__)
    d = os.path.join(here, subdir)
    names = [name for name in os.listdir(d) if not name.startswith('.')]
    return os.path.join(d, random.choice(names))

def get_sample_text(linecount=2, allow_empty=False):
    fn = get_sample_filename()

    sz = os.path.getsize(fn)
    pos = random.randint(0, sz - 80 * linecount)

    f = open(fn, 'r')
    f.seek(pos)
    f.readline()

    text = []
    while len(text) < linecount:
        line = f.readline()
        if not line:
            # end of file
            break
        line = line.strip()
        if not line and not allow_empty:
            continue
        if ignore_line_re.search(line):
            continue
        text.append(line)

    return '\n'.join(text)

def get_sample_html(linecount=None):
    if linecount is None:
        linecount = random.randint(5, 30)
    text = get_sample_text(linecount=linecount, allow_empty=True)
    paragraphs = text.split('\n\n')
    res = []
    for p in paragraphs:
        words = [escape(word) for word in p.split()]
        if words:
            i = random.randint(0, len(words) - 1)
            words[i] = '<em>%s</em>' % words[i]
        res.append('<p>%s</p>' % ' '.join(words))
    return '\n\n'.join(res)

def generate_title(prefix):
    wordcount = random.randint(2, 5)

    fn = get_sample_filename()

    title_words = title_word_cache.get(fn)
    if title_words is None:
        f = open(fn, 'r')
        text = f.read()
        f.close()
        word_set = set()
        for word in title_word_re.findall(text):
            if "'" not in word:
                word_set.add(word)
        title_words = list(word_set)
        title_word_cache[fn] = title_words

    lst = []
    lst.append('(%s%05d)' % (prefix, random.randint(0, 99999)))
    for i in range(wordcount):
        lst.append(random.choice(title_words))

    return ' '.join(lst)


def _parse_form_errors(response_body):
    """Screen-scrape form errors (for debugging)."""
    errors = []
    doc = lxml.html.fromstring(response_body)
    for field_elem in doc.findall('*//fieldset'):
        field_id = field_elem.attrib.get('id')
        if not field_id:
            continue
        error_elem = field_elem.find('.//*[@class="errorMessage"]')
        if error_elem is not None:
            errors.append("%s: %s." % (field_id, error_elem.text))
    return ' '.join(errors)

def _parse_add_response(request, response, parent):
    """If the add form succeeded, return the object added.

    Raises an exception if the add form did not redirect as expected.
    """
    parent_url = model_url(parent, request)
    if not response.location:
        # The add operation failed.  Try to extract the error messages.
        errors = _parse_form_errors(response.body)
        raise AssertionError(
            "Add operation failed. %s" % errors)
    if not response.location.startswith(parent_url):
        raise AssertionError("URL mismatch: %r is not a parent of %r"
            % (parent_url, response.location))
    s = response.location[len(parent_url):]
    if s.startswith('/'):
        s = s[1:]
    obj_id = s.split('/', 1)[0].split('?', 1)[0]
    return parent[obj_id]

class FauxPost(dict):
    def getall(self, key):
        return self.get(key, ())


def add_sample_community(site, add_content=True):
    communities = site['communities']

    title = generate_title('SampleC')
    log.info('adding community %s', title)

    request = testing.DummyRequest()
    request.environ.update(DEFAULT_ENV)
    request.POST = FauxPost(request.POST)
    request.POST['title'] = title
    request.POST['description'] = get_sample_text(2)
    request.POST['text'] = get_sample_html()
    request.POST['tags'] = ['sample']
    request.POST['security_state'] = 'public'
    for key in ('blog', 'wiki', 'calendar', 'files'):
        request.POST[key] = True
    request.POST['form.submitted'] = True

    response = add_community_view(communities, request)
    community = _parse_add_response(request, response, communities)

    if add_content:
        for i in range(random.randint(1, 10)):
            add_sample_blog_entry(community)
        for i in range(random.randint(1, 10)):
            add_sample_wiki_page(community)
        for i in range(random.randint(1, 10)):
            add_sample_calendar_event(community)
        for i in range(random.randint(1, 10)):
            add_sample_file(community, i)

    return community


def add_sample_blog_entry(community):
    blog = community['blog']

    title = generate_title('SampleB')
    log.info('adding blog entry %s', title)

    request = testing.DummyRequest()
    request.environ.update(DEFAULT_ENV)
    request.POST = FauxPost(request.POST)
    request.POST['title'] = title
    request.POST['text'] = get_sample_html()
    request.POST['sendalert'] = False
    request.POST['security_state'] = 'inherits'
    request.POST['tags'] = ['sample']
    request.POST['form.submitted'] = True

    response = add_blogentry_view(blog, request)
    entry = _parse_add_response(request, response, blog)
    return entry


def add_sample_wiki_page(community):
    wiki = community['wiki']

    title = generate_title('SampleW')
    log.info('adding wiki page %s', title)

    request = testing.DummyRequest()
    request.environ.update(DEFAULT_ENV)
    request.POST = FauxPost(request.POST)
    request.POST['title'] = title
    request.POST['text'] = get_sample_html()
    request.POST['security_state'] = 'inherits'
    request.POST['tags'] = ['sample']
    request.POST['form.submitted'] = True

    response = add_wikipage_view(wiki, request)
    page = _parse_add_response(request, response, wiki)

    # add a link to the new page
    wiki['front_page'].text += u'<p>((%s))</p>' % page.title

    return page


def add_sample_calendar_event(community):
    calendar = community['calendar']

    title = generate_title('SampleE')
    log.info('adding calendar event %s', title)

    # Choose a random day and hour in the current month of the
    # current year.
    now = datetime.datetime.now()
    start = now.replace(
        day=random.randint(1, 28),
        hour=random.randint(9, 17),
        minute=random.choice((0, 15, 30, 45)),
        second=0,
        )
    end = start.replace(hour = start.hour + 1)
    start_str = start.strftime('%m/%d/%Y %H:%M')
    end_str = end.strftime('%m/%d/%Y %H:%M')

    request = testing.DummyRequest()
    request.environ.update(DEFAULT_ENV)
    request.POST = FauxPost(request.POST)
    request.POST['title'] = title
    request.POST['virtual_calendar'] = ''
    request.POST['startDate'] = start_str
    request.POST['endDate'] = end_str
    request.POST['location'] = 'Sample Location'
    request.POST['attendees'] = ''
    request.POST['contact_name'] = ''
    request.POST['contact_email'] = ''
    request.POST['text'] = get_sample_html()
    request.POST['security_state'] = 'inherits'
    request.POST['tags'] = ['sample']
    request.POST['form.submitted'] = True

    response = add_calendarevent_view(calendar, request)
    event = _parse_add_response(request, response, calendar)
    return event


def add_sample_file(community, i):
    files = community['files']

    title = generate_title('SampleF')
    log.info('adding file %s', title)

    filename = get_sample_filename(subdir='samplefiles')
    stream = open(filename, 'rb')

    class FakeFieldStorage:
        pass
    fs = FakeFieldStorage()
    fs.filename = 'sample%d-%s' % (i, os.path.basename(filename))
    fs.file = stream
    fs.type, _ = mimetypes.guess_type(filename)

    request = testing.DummyRequest()
    request.environ.update(DEFAULT_ENV)
    request.POST = FauxPost(request.POST)
    request.POST['title'] = title
    request.params['file'] = fs
    request.POST['security_state'] = 'inherits'
    request.POST['tags'] = ['sample']
    request.POST['form.submitted'] = True

    response = add_file_view(files, request)
    file = _parse_add_response(request, response, files)

    stream.close()

    return file


def add_sample_users(site):
    profiles = site['profiles']
    users = site.users

    for login, firstname, lastname, email, groups in [
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
        ]:
        if users.get(login=login) is None:
            users.add(login, login, login, groups)
        if not login in profiles:
            profile = profiles[login] = create_content(
                IProfile,
                firstname=firstname,
                lastname=lastname,
                email=email,
                )
            workflow = get_workflow(IProfile, 'security', profiles)
            if workflow is not None:
                workflow.initialize(profile)
