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

from zope.interface import Attribute
from zope.interface import Interface

class IMimeInfo(Interface):
    """ Utility for getting mimeinfo such as icon filename
    """
    def __call__(mimetype):
        """ Return a dictionary in the form

        {'small_icon_name':<relative_filename>, 'title':<title>}

        to service mimetype graphical information """


class IMailinTextScrubber(Interface):
    """ Utility for cleaning text of mail-in content.
    """
    def __call__(text, mimetype=None):
        """ Return scrubbed version of 'text'.

        o 'mimetype', if passed, will be the MIME type of the part from
          which 'text' was extracted.
        """

class IKarlDates(Interface):
    """ Utility for various representations of a date
    """
    def __call__(date, flavor):
        """ Given DateTime, return string formmated in various flavors """

class IRandomId(Interface):
    """ A utility which returns a random identifier string """
    def __call__(size=6):
        """ Return the ranomly generated string of ``size`` characters"""

#XXX Does this go here? 
class IAlert(Interface):
    """An alert message, suitable for emailing or digesting."""
  
    mfrom = Attribute("Email address of sender.")
    mto = Attribute("Sequence of email addresses for all recipients.")
    message = Attribute("An instance of email.message.Message to be mailed.")
    digest = Attribute("""Boolean, can be set by caller to indicate alert
                       should be formatted for digest.""")
    
class IAlerts(Interface):
    """A utility which emits activity alerts to community members.
    """
    def emit(context, factory, request):
        """Emits an alert.
        
        For each user to be alerted will either send the alert immediately, 
        add to a digest queue, or not send at all, according to member
        preferences.
        
          o context is place in model tree in which alert is occuring.
          o factory is a callable which can generate an IAlert instance and
            has the signature: (context, profile) where context is the same
            object as above and profile is the user being alerted.
        """
        
    def send_digests(context):
        """Iterates over all user profiles and sends digested alerts.  Will
        generally be called by a console script which in turn is called by
        cron.  
        
        o context can be an model object in the site hierarchy, usually the
          root.
          
        """