from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import ACLDenied
from pyramid.threadlocal import get_current_request

from karl.utils import find_site
from karl.utils import find_profiles


class RestrictedACLAuthorizationPolicy(ACLAuthorizationPolicy):

    def permits(self, context, principals, permission):
        """ Check whitelist and blacklist before passing on to regular
        permission check.
        """
        if self.restricted_access(context, principals):
            return ACLDenied('<default deny>',
                             '<Access to the site forbidden for this user>',
                             permission,
                             principals,
                             context)
        return super(RestrictedACLAuthorizationPolicy,
                     self).permits(context, principals, permission)

    def principals_allowed_by_permission(self, context, permission):
        """ Check whitelist and blacklist before passing on to regular
        allowed principals check.
        """
        allowed = super(RestrictedACLAuthorizationPolicy,
                        self).principals_allowed_by_permission(context, permission)
        remove = []
        for principal in allowed:
            if self.restricted_access(context, [principal]):
                remove.append(principal)
        for principal in remove:
            allowed.remove(principal)
        return allowed

    def restricted_access(self, context, principals):
        restricted = False
        site = find_site(context)
        whitelist = getattr(site, 'access_whitelist', [])
        blacklist = getattr(site, 'access_blacklist', [])
        is_admin = u'group.KarlAdmin' in principals
        if (whitelist or blacklist) and not is_admin:
            profile = self._get_profile(context, principals)
            if profile and '@' in profile.email:
                domain = '@%s' % profile.email.split('@')[1]
                if domain in blacklist:
                    restricted = True
            for principal in principals:
                if principal in blacklist:
                    restricted = True
                    break
            if whitelist:
                white = False
                if profile and '@' in profile.email:
                    domain = '@%s' % profile.email.split('@')[1]
                    if domain in whitelist:
                        white = True
                for principal in principals:
                    if principal in whitelist:
                        white = True
                        break
                if not white:
                    restricted = True
            if restricted:
                request = get_current_request()
                request.session['access_blacklisted'] = True
        return restricted

    def _get_profile(self, context, principals):
        profile = None
        userid = None
        profiles = find_profiles(context)
        for principal in principals:
            if not principal.startswith('group.') and not principal.startswith('system.'):
                userid = principal
                break
        if userid is not None:
            profile = profiles.get(userid)
        return profile
