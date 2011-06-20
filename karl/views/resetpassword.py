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

from karl.models.interfaces import ICatalogSearch
from karl.models.interfaces import IProfile
from karl.utils import find_profiles
from karl.utils import find_site
from karl.utils import find_users
from karl.utils import get_setting
from karl.views.api import TemplateAPI
from karl.views.api import xhtml
from karl.views.forms import validators as karlvalidators
from karl.views.forms import widgets as karlwidgets
from repoze.bfg.chameleon_zpt import get_template
from repoze.bfg.chameleon_zpt import render_template
from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.formish import ValidationError
from repoze.bfg.url import model_url
from repoze.postoffice.message import Message
from repoze.sendmail.interfaces import IMailDelivery
from validatish import validator
from webob.exc import HTTPFound
from zope.component import getAdapter
from zope.component import getUtility
import datetime
import formish
import random
import schemaish
import urllib


try:
    from hashlib import sha1
except ImportError:
    from sha import new as sha1


max_reset_timedelta = datetime.timedelta(3)  # days

email_field = schemaish.String(
    validator=validator.All(validator.Required(),
                            validator.Email(),
                            )
    )

class ResetRequestFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def form_fields(self):
        return [('email', email_field)]

    def form_widgets(self, fields):
        return {'email': formish.Input(empty='')}

    def __call__(self):
        page_title = u"Forgot Password Request"
        snippets = get_template('forms/templates/snippets.pt')
        snippets.doctype = xhtml
        blurb_macro = snippets.macros['reset_request_blurb']
        api = TemplateAPI(self.context, self.request, page_title)
        return {'api': api, 'blurb_macro': blurb_macro}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        context = self.context
        request = self.request
        system_name = get_setting(context, 'system_name', 'KARL')
        address = converted['email']
        if address:
            address = address.lower()

        search = getAdapter(context, ICatalogSearch)
        count, docids, resolver = search(
            interfaces=[IProfile], email=[address])

        users = find_users(context)
        for docid in docids:
            profile = resolver(docid)
            if profile is None:
                continue
            userid = profile.__name__
            user = users.get_by_id(userid)
            if user is None:
                continue
            # found the profile and user
            break
        else:
            raise ValidationError(**{"email":
                "%s has no account with the email address: %s" %
                (system_name, address)})

        groups = user['groups']
        if groups and 'group.KarlStaff' in groups:
            # because staff accounts are managed centrally, staff
            # must use the forgot_password_url if it is set.
            forgot_password_url = get_setting(
                context, 'forgot_password_url')
            if forgot_password_url:
                came_from = model_url(context, request, "login.html")
                url = '%s?email=%s&came_from=%s' % (
                    forgot_password_url, urllib.quote_plus(address),
                    urllib.quote_plus(came_from))
                return HTTPFound(location=url)

        request_password_reset(user, profile, request)

        url = model_url(context, request, 'reset_sent.html') + (
            '?email=%s' % urllib.quote_plus(address))
        return HTTPFound(location=url)

def request_password_reset(user, profile, request):
    profile.password_reset_key = sha1(
        str(random.random())).hexdigest()
    profile.password_reset_time = datetime.datetime.now()
    context = find_site(profile)
    reset_url = model_url(
        context, request, "reset_confirm.html",
        query=dict(key=profile.password_reset_key))

    # send email
    mail = Message()
    system_name = get_setting(context, 'system_name', 'KARL')
    admin_email = get_setting(context, 'admin_email')
    mail["From"] = "%s Administrator <%s>" % (system_name, admin_email)
    mail["To"] = "%s <%s>" % (profile.title, profile.email)
    mail["Subject"] = "%s Password Reset Request" % system_name
    body = render_template(
        "templates/email_reset_password.pt",
        login=user['login'],
        reset_url=reset_url,
        system_name=system_name,
    )

    if isinstance(body, unicode):
        body = body.encode("UTF-8")

    mail.set_payload(body, "UTF-8")
    mail.set_type("text/html")

    recipients = [profile.email]
    mailer = getUtility(IMailDelivery)
    mailer.send(recipients, mail)

def reset_sent_view(context, request):
    page_title = 'Password Reset Instructions Sent'
    api = TemplateAPI(context, request, page_title)
    return render_template_to_response(
        'templates/reset_sent.pt',
        api=api,
        email=request.params.get('email'),
        )


class ResetConfirmFormController(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def form_fields(self):
        min_pw_length = get_setting(None, 'min_pw_length')
        login_field = schemaish.String(validator=validator.Required())
        password_field = schemaish.String(
            validator=validator.All(
                validator.Required(),
                karlvalidators.PasswordLength(min_pw_length)),
            title='New Password')
        fields = [('login', login_field),
                  ('password', password_field),
                  ]
        return fields

    def form_widgets(self, fields):
        widgets = {'login': formish.Input(empty=''),
                   'password': karlwidgets.KarlCheckedPassword()}
        return widgets

    def __call__(self):
        key = self.request.params.get('key')
        if not key or len(key) != 40:
            api = TemplateAPI(self.context, self.request,
                              'Password Reset URL Problem')
            return render_template_to_response('templates/reset_failed.pt',
                                               api=api)
        snippets = get_template('forms/templates/snippets.pt')
        snippets.doctype = xhtml
        blurb_macro = snippets.macros['reset_confirm_blurb']
        api = TemplateAPI(self.context, self.request, 'Reset Password')
        return {'api': api, 'blurb_macro': blurb_macro}

    def handle_cancel(self):
        return HTTPFound(location=model_url(self.context, self.request))

    def handle_submit(self, converted):
        try:
            context = self.context
            request = self.request
            key = request.params.get('key')
            if not key or len(key) != 40:
                e = ResetFailed()
                e.page_title = 'Password Reset URL Problem'
                raise e
            users = find_users(context)
            user = users.get_by_login(converted['login'])
            if user is None:
                raise ValidationError(login='No such user account exists')
            userid = user.get('id')
            if userid is None:
                userid = user['login']

            profiles = find_profiles(context)
            profile = profiles.get(userid)
            if profile is None:
                raise ValidationError(login='No such profile exists')

            if key != getattr(profile, 'password_reset_key', None):
                e = ResetFailed()
                e.page_title = 'Password Reset Confirmation Problem'
                raise e

            now = datetime.datetime.now()
            t = getattr(profile, 'password_reset_time', None)
            if t is None or now - t > max_reset_timedelta:
                e = ResetFailed()
                e.page_title = 'Password Reset Confirmation Key Expired'
                raise e

            # The key matched.  Clear the key and reset the password.
            profile.password_reset_key = None
            profile.password_reset_time = None
            password = converted['password'].encode('UTF-8')
            users.change_password(userid, password)

            page_title = 'Password Reset Complete'
            api = TemplateAPI(context, request, page_title)
            return render_template_to_response(
                'templates/reset_complete.pt',
                api=api,
                login=converted['login'],
                password=converted['password'],
                )

        except ResetFailed, e:
            api = TemplateAPI(context, request, e.page_title)
            return render_template_to_response('templates/reset_failed.pt',
                                               api=api)

class ResetFailed(Exception):
    pass
