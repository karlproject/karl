#
# Data for the OSI offices
#
import pkg_resources

from zope.interface import implements

from karl.bootstrap.interfaces import IInitialOfficeData

from pyramid.security import Allow

from karl.content.views.intranets import sample_feature
from karl.security.policy import ADMINISTRATOR_PERMS
from karl.security.policy import GUEST_PERMS
from karl.security.policy import NO_INHERIT

nyc_forums = [
    {'id': 'nyc-personals', 'title': 'New York City Personals'},
    {'id': 'nyc-news', 'title': 'New York News'},
    {'id': 'nyc-helpwanted', 'title': 'New York Help Wanted'},
    {'id': 'nyc-policies-and-procedures',
     'title': 'New York Policies and Procedures'},
    {'id': 'nyc-apartment-seekers',
     'title': 'New York Apartment Seekers'},
]

nyc_navmenu = """<div>
    <div class="menu">
        <h3>About OSI</h3>

        <ul class="nav">
            <li>
                <a href="/offices/nyc/about-osi/about-osi-and-the-soros-foundations-network.html"
                    target="" title="">About OSI &amp; Soros Foundations Network</a>
            </li>
            <li>
                <a href="/offices/nyc/about-osi/about-george-soros.html" target="" title="">About
                    George Soros</a>
            </li>

            <li>
                <a href="/people/" target="" title="">Network Directory</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Resources</h3>
        <ul class="nav">

            <li class="submenu">
                <a href="/offices/nyc/referencemanuals" target="" title="">Administration</a>
                <ul class="level2">
                    <li>
                        <a href="/offices/nyc/referencemanuals/communications" target="" title=""
                            >Communications</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/facilities-management" target=""
                            title="">Facilities Management</a>

                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/finance" target="" title=""
                            >Finance</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/legal" target="" title="">Legal</a>
                    </li>
                    <li>

                        <a href="/offices/nyc/referencemanuals/grants-management" target="" title=""
                            >Grants Management</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/human-resources" target="" title=""
                            >Human Resources</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/information-systems" target=""
                            title="">Information Systems</a>

                    </li>
                    <li>
                        <a
                            href="/offices/nyc/referencemanuals/facilities-management/records-management-program"
                            target="" title="">Records Management</a>
                    </li>
                    <li>
                        <a
                            href="/offices/nyc/referencemanuals/travel-authorization-and-security-policies"
                            target="" title="">Travel Authorization and Security</a>
                    </li>
                    <li>

                        <a
                            href="/offices/nyc/referencemanuals/travel-expenses-guidelines-and-procedures"
                            target="" title="">Travel and Expenses</a>
                    </li>
                </ul>
            </li>
            <li>
                <a href="/offices/nyc/whats-for-lunch">What's for Lunch?</a>
            </li>
            <li>

                <a href="/offices/forums/all_forums.html">Message Boards</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Tools &amp; Services</h3>
        <ul class="nav">

            <li>
                <a
                    href="/wrap_external_link?external_url=https://prs.soros.org/businesscenter/loginvalidate.aspx"
                    target="_blank" title="Business Center">Business Center</a>
            </li>
            <li class="submenu">
                <a
                    href="/wrap_external_link?external_url=http://osi-ny.soros.org/channel_select.cfm?RequestType=Events&amp;amp;Pulldown=Yes"
                    target="_blank" title="Reserve and view conference rooms in New York">Meeting
                    Calendar</a>
                <ul class="level2">
                    <li>
                        <a
                            href="/wrap_external_link?external_url=http://osi-ny.soros.org/channel_select.cfm?RequestType=CalendarOfEvents&amp;Pulldown=Yes&amp;Channel=Events"
                            target="_blank" title="">Calendar of Events</a>

                    </li>
                    <li>
                        <a
                            href="/wrap_external_link?external_url=http://osi-ny.soros.org/events/index.cfm?RequestType=TodaysEvents"
                            target="_blank" title="">Today's Events</a>
                    </li>
                    <li>
                        <a
                            href="/wrap_external_link?external_url=http://osi-ny.soros.org/events/step1.cfm?RequestType=ConferenceReservation"
                            target="_blank" title="">Reserve a Room</a>
                    </li>
                    <li>

                        <a
                            href="/wrap_external_link?external_url=http://osi-ny.soros.org/events/at-a-glance.cfm?RequestType=MeetingPlanner"
                            target="_blank" title="">Meeting Planner</a>
                    </li>
                </ul>
            </li>
            <li>
                <a
                    href="/wrap_external_link?external_url=http://osi-ny.soros.org/troubletkt/step2.cfm?cat=Web"
                    target="_blank" title="Request help with a website">Web Requests</a>
            </li>
            <li>

                <a
                    href="/wrap_external_link?external_url=http://osi-ny.soros.org/systems_hw_request/order/step1.cfm?RequestType=HardwareSoftwareRequest"
                    target="_blank" title="Request a new computer, monitor, or mouse"
                    >Hardware/Software Requests</a>
            </li>
            <li>
                <a
                    href="/wrap_external_link?external_url=https://prs.soros.org/travelrequest/loginvalidate.aspx"
                    target="_blank" title="Travel Requests">Travel Requests</a>
            </li>
            <li class="submenu">
                <a href="" target="" title="">Records Management</a>

                <ul class="level2">
                    <li>
                        <a href="http://osi-ny.soros.org/content/records_mgmt/form.cfm"
                            target="_blank" title="">Inventory Sheet</a>
                    </li>
                    <li>
                        <a href="http://osi-ny.soros.org/content/records_mgmt/search.cfm"
                            target="_blank" title="">Find a Record</a>
                    </li>
                </ul>

            </li>
            <li class="submenu">
                <a href="#" target="" title="Research and Reference">Research &amp;
                    Reference</a>
                <ul class="level2">
                    <li>
                        <a href="http://imgenie.soros.org/InmagicGenie/opac.aspx" target="_blank"
                            title="">Library Databases</a>
                    </li>

                    <li>
                        <a href="http://snap.archivum.ws/dspace/community-list" target="_blank"
                            title="Soros Network Archival Portal">SNAP</a>
                    </li>
                </ul>
            </li>
            <li>
                <a href="http://interactweb.soros.org/InterAction" target="_blank"
                    title="Find Contacts">Interaction</a>
            </li>

        </ul>
    </div>
    <div class="menu">
        <h3>Help Desk</h3>
        <ul class="nav">
            <li>
                <a
                    href="/wrap_external_link?external_url=http://osi-ny.soros.org/troubletkt/step1.cfm"
                    target="_blank" title="Request technical assistance">Trouble Ticket</a>
            </li>

            <li class="submenu">
                <a href="/offices/nyc/help-desk/user-manuals" target="" title="">Phone &amp;
                    Voicemail</a>
                <ul class="level2">
                    <li>
                        <a href="/offices/nyc/help-desk/user-manuals/telephone_navigation.pdf"
                            target="" title="">Using Voicemail</a>
                    </li>
                    <li>

                        <a href="/offices/nyc/help-desk/user-manuals/using-telephone" target=""
                            title="">Using Telephone</a>
                    </li>
                    <li>
                        <a
                            href="/offices/nyc/help-desk/user-manuals/conference-calls/conference-calls-introduction"
                            target="" title="">Conference Call Reservations</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/help-desk/faqs/unified-messaging-solution" target=""
                            title="">UMS, Unified Messaging</a>

                    </li>
                </ul>
            </li>
            <li>
                <a href="/offices/nyc/help-desk/user-manuals/checking-webmail" target=""
                    title="Checking your email via the web">Checking Webmail</a>
            </li>
            <li class="submenu">
                <a href="/offices/nyc/help-desk/more-systems-help" target="" title="">Login
                    &amp; Password</a>

                <ul class="level2">
                    <li>
                        <a href="/offices/nyc/help-desk/more-systems-help/login-help" target=""
                            title="">Login help</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/help-desk/more-systems-help/changing-password"
                            target="" title="">Changing Password</a>
                    </li>
                </ul>

            </li>
            <li>
                <a href="/communities/about-karl/wiki/karl-user-manual" target="_blank"
                    title="Help using KARL">Karl User Manual</a>
            </li>
        </ul>
    </div>
</div>
"""

budapest_forums = [
    {'id': 'budapest-personals', 'title': 'Budapest Personals'},
    {'id': 'budapest-news', 'title': 'Budapest News'},
    {'id': 'budapest-events', 'title': 'Budapest Events'},
]

baltimore_navmenu = """<div>
    <div class="menu">
        <h3>About OSI</h3>

        <ul class="nav">
            <li>
                <a href="/offices/nyc/about-osi/about-osi-and-the-soros-foundations-network.html">About OSI &amp; Soros Foundations Network</a>
            </li>
            <li>
                <a href="/offices/nyc/about-osi/about-george-soros.html">About George Soros</a>
            </li>

            <li>
                <a href="/people/">Network Directory</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Resources</h3>
        <ul class="nav">

            <li class="submenu">
                <a href="/offices/nyc/referencemanuals">Administration</a>
                <ul class="level2">
                    <li>
                        <a href="/offices/nyc/referencemanuals/communications">Communications</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/facilities-management">Facilities Management</a>

                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/finance">Finance</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/legal">Legal</a>
                    </li>
                    <li>

                        <a href="/offices/nyc/referencemanuals/grants-management">Grants
                            Management</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/human-resources">Human
                            Resources</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/information-systems">Information Systems</a>

                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/facilities-management/records-management-program">Records Management</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/travel-expenses-guidelines-and-procedures">Travel and Expenses</a>
                    </li>
                    <li>

                        <a href="/offices/nyc/referencemanuals/travel-authorization-and-security-policies">Travel Authorization and Security</a>
                    </li>
                </ul>
            </li>
            <li>
                <a href="/offices/forums/all_forums.html">Message Boards</a>
            </li>
        </ul>

    </div>
    <div class="menu">
        <h3>Tools &amp; Services</h3>
        <ul class="nav">
            <li>
                <a href="/wrap_external_link?external_url=https://prs.soros.org/businesscenter/loginvalidate.aspx" target="_blank" title="Business Center">Business Center</a>
            </li>

            <li class="submenu">
                <a href="/wrap_external_link?external_url=http://osi-ny.soros.org/channel_select.cfm?Pulldown=Yes&amp;Channel=Events" target="_blank" title="Reserve and view conference rooms in New York">NY Events Calendar</a>
                <ul class="level2">
                    <li>
                        <a href="/wrap_external_link?external_url=http://osi-ny.soros.org/events/step1.cfm?RequestType=ConferenceReservation" target="_blank">Conference Room Reservation</a>
                    </li>
                    <li>
                        <a href="/wrap_external_link?external_url=http://osi-ny.soros.org/events/at-a-glance.cfm?RequestType=MeetingPlanner" target="_blank">Meeting Planner</a>

                    </li>
                </ul>
            </li>
            <li>
                <a href="/wrap_external_link?external_url=http://osi-ny.soros.org/troubletkt/step2.cfm?cat=Web" target="_blank" title="Request help with a website">Web Requests</a>
            </li>
            <li>
                <a href="/wrap_external_link?external_url=http://osi-ny.soros.org/systems_hw_request/order/step1.cfm?RequestType=HardwareSoftwareRequest" target="_blank" title="Request a new computer, monitor, or mouse">Hardware/Software Requests</a>

            </li>
            <li>
                <a href="/wrap_external_link?external_url=https://prs.soros.org/travelrequest/loginvalidate.aspx" target="_blank" title="Travel Requests">Travel Requests</a>
            </li>
            <li class="submenu">
                <a href="#" title="Research and Reference">Research &amp; Reference</a>
                <ul class="level2">

                    <li>
                        <a href="http://imgenie.soros.org/InmagicGenie/opac.aspx" target="_blank">Library Databases</a>
                    </li>
                    <li>
                        <a href="http://snap.archivum.ws/dspace/community-list" target="_blank" title="Soros Network Archival Portal">SNAP</a>
                    </li>
                </ul>
            </li>

            <li>
                <a href="http://interactweb.soros.org/InterAction" target="_blank" title="Find Contacts">Interaction</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Help Desk</h3>
        <ul class="nav">

            <li>
                <a href="/wrap_external_link?external_url=http://osi-ny.soros.org/troubletkt/step1.cfm" target="_blank" title="Request technical assistance">Trouble Ticket</a>
            </li>
            <li>
                <a href="/offices/nyc/help-desk/user-manuals/checking-webmail" title="Checking your email via the web">Checking Webmail</a>
            </li>
            <li class="submenu">
                <a href="/offices/nyc/help-desk/more-systems-help">Login &amp; Password</a>

                <ul class="level2">
                    <li>
                        <a href="/offices/nyc/help-desk/more-systems-help/login-help">Login help</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/help-desk/more-systems-help/changing-password">Changing Password</a>
                    </li>
                </ul>

            </li>
            <li>
                <a href="/communities/about-karl/wiki/karl-user-manual" target="_blank" title="Help using KARL">Karl User Manual</a>
            </li>
        </ul>
    </div>
</div>
"""

brussels_navmenu = """<div>
    <div class="menu">
        <h3>About OSI</h3>

        <ul class="nav">
            <li>
                <a href="/offices/nyc/about-osi/about-osi-and-the-soros-foundations-network.html">About OSI &amp; Soros Foundations Network</a>
            </li>
            <li>
                <a href="/offices/nyc/about-osi/about-george-soros.html">About George Soros</a>
            </li>

            <li>
                <a href="/people/">Network Directory</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Resources</h3>
        <ul class="nav">

            <li class="submenu">
                <a href="/offices/brussels/referencemanuals">Administration</a>
                <ul class="level2">
                    <li>
                        <a href="/offices/brussels/referencemanuals/human-resources">Human Resources</a>
                    </li>
                    <li>
                        <a href="/offices/brussels/referencemanuals/office-management">Office Management</a>

                    </li>
                    <li>
                        <a href="/offices/brussels/referencemanuals/travel">Travel</a>
                    </li>
                </ul>
            </li>
            <li>
                <a href="/offices/files/referencemanuals/travel-authorization-and-security-policies">Travel Authorization and Security Policies</a>

            </li>
            <li>
                <a href="/offices/brussels/papers-articles-speeches">Papers, Articles, Speeches</a>
            </li>
            <li>
                <a href="/offices/brussels/annual-strategy/">Annual Strategy</a>
            </li>
            <li>

                <a href="/offices/forums/all_forums.html">Message Boards</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Tools &amp; Services</h3>
        <ul class="nav">

            <li>
                <a href="/wrap_external_link?external_url=https://businesscenter.osi.hu/login.aspx" target="_blank" title="Business Center">Business Center</a>
            </li>
            <li>
                <a href="/wrap_external_link?external_url=http://osi-ny.soros.org/troubletkt/step2.cfm?cat=Web" target="_blank" title="Request help with a website">Web Requests</a>
            </li>
            <li>
                <a href="http://snap.archivum.ws/dspace/community-list" target="_blank" title="Soros Network Archival Portal">SNAP</a>

            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Help Desk</h3>
        <ul class="nav">
            <li>
                <a href="/offices/nyc/help-desk/login-problems/karl-user-name-and-password">KARL Login Help</a>

            </li>
            <li>
                <a href="/communities/about-karl/wiki/karl-user-manual">KARL User Manual</a>
            </li>
        </ul>
    </div>
</div>
"""

budapest_navmenu = """<div>
    <div class="menu">
        <h3>About OSI</h3>

        <ul class="nav">
            <li>
                <a href="/offices/nyc/about-osi/about-osi-and-the-soros-foundations-network.html">About OSI &amp; Soros Foundations Network</a>
            </li>
            <li>
                <a href="/offices/nyc/about-osi/about-george-soros.html">About George Soros</a>
            </li>

            <li>
                <a href="/people/">Network Directory</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Resources</h3>
        <ul class="nav">

            <li class="submenu">
                <a href="/offices/budapest/referencemanuals">Administration</a>
                <ul class="level2">
                    <li>
                        <a href="/offices/budapest/referencemanuals/communications">Communications</a>
                    </li>
                    <li>
                        <a href="/offices/budapest/referencemanuals/contract-management">ContractSQL</a>

                    </li>
                    <li>
                        <a href="/offices/budapest/referencemanuals/finance-adminconsult">Finance (AdminConsult)</a>
                    </li>
                    <li>
                        <a href="/offices/budapest/referencemanuals/grants-management">Grants Management</a>
                    </li>
                    <li>

                        <a href="/offices/budapest/referencemanuals/human-resources">Human Resources</a>
                    </li>
                    <li>
                        <a href="/offices/budapest/referencemanuals/information-systems">Information Systems</a>
                    </li>
                    <li>
                        <a href="/offices/budapest/referencemanuals/office-management">Office Management</a>

                    </li>
                    <li>
                        <a href="/offices/budapest/referencemanuals/records-management">Records Management</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/travel-authorization-and-security-policies">Travel Authorization and Security</a>
                    </li>
                </ul>

            </li>
            <li>
                <a href="/offices/budapest/budapest-employee-resources/forms">Forms</a>
            </li>
            <li>
                <a href="/offices/forums/all_forums.html">Message Boards</a>
            </li>
        </ul>

    </div>
    <div class="menu">
        <h3>Tools &amp; Services</h3>
        <ul class="nav">
            <li>
                <a href="/wrap_external_link?external_url=https://businesscenter.osi.hu/login.aspx" target="_blank">Business Center</a>
            </li>

            <li>
                <a href="/wrap_external_link?external_url=https://businesscenter.osi.hu/TravelRequest/LoginValidate.aspx" target="_blank" title="Travel Requests">Travel Requests</a>
            </li>
            <li>
                <a href="/wrap_external_link?external_url=http://osi-ny.soros.org/troubletkt/step2.cfm?cat=Web" target="_blank" title="Request help with a website">Web Requests</a>
            </li>
            <li>
                <a href="http://snap.archivum.ws/dspace/community-list" target="_blank" title="Soros Network Archival Portal">SNAP</a>

            </li>
            <li>
                <a href="/offices/budapest/useful-links" title="Useful links for Budapest office users">Useful Links</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Help Desk</h3>

        <ul class="nav">
            <li>
                <a href="/wrap_external_link?external_url=https://businesscenter.osi.hu/troubleticket/ " target="_blank" title="Request technical assistance">Trouble Ticket</a>
            </li>
            <li class="submenu">
                <a href="#">Login &amp; Password</a>
                <ul class="level2">

                    <li>
                        <a href="/offices/budapest/help-desk/karl-user-name-and-password">Karl Login</a>
                    </li>
                    <li>
                        <a href="/offices/budapest/help-desk/network-login">Network
                            Login</a>
                    </li>
                </ul>
            </li>

            <li class="submenu">
                <a href="/offices/budapest/help-desk/user-manuals">Phone &amp; Voicemail</a>
                <ul class="level2">
                    <li>
                        <a href="/offices/budapest/help-desk/user-manuals/VoiceMail_EN.pdf">Using Voicemail English</a>
                    </li>
                    <li>

                        <a href="/offices/budapest/help-desk/user-manuals/VoiceMail_HU.pdf">Using Voicemail Hungarian</a>
                    </li>
                </ul>
            </li>
            <li>
                <a href="/offices/budapest/help-desk/user-manuals/checking-webmail" title="Checking your email via the web">Checking Webmail</a>
            </li>
            <li>

                <a href="/communities/about-karl/wiki/karl-user-manual">KARL User Manual</a>
            </li>
        </ul>
    </div>
</div>
"""

london_navmenu = """<div>
    <div class="menu">
        <h3>About OSI</h3>

        <ul class="nav">
            <li>
                <a href="/offices/nyc/about-osi/about-osi-and-the-soros-foundations-network.html">About OSI &amp; Soros Foundations Network</a>
            </li>
            <li>
                <a href="/offices/nyc/about-osi/about-george-soros.html">About George Soros</a>
            </li>

            <li>
                <a href="/people/">Network Directory</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Resources</h3>
        <ul class="nav">

            <li class="submenu">
                <a href="#">London Resources</a>
                <ul class="level2">
                    <li>
                        <a href="/communities/moving-to-and-living-in-london">Moving to
                            and Living in London</a>
                    </li>
                    <li>
                        <a href="/offices/london/london-employee-resources/hotels-in-london">Hotels in London</a>

                    </li>
                    <li>
                        <a href="/offices/london/referencemanuals/cambridge-house">Cambridge House</a>
                    </li>
                </ul>
            </li>
            <li class="submenu">
                <a href="/offices/london/referencemanuals">Administration</a>

                <ul class="level2">
                    <li>
                        <a href="/offices/london/referencemanuals/human-resources">Human
                            Resources</a>
                    </li>
                    <li>
                        <a href="/offices/london/referencemanuals/travel">Travel</a>
                    </li>
                    <li>

                        <a href="/offices/files/referencemanuals/travel-authorization-and-security-policies">Travel Authorization and Security</a>
                    </li>
                </ul>
            </li>
            <li>
                <a href="/offices/forums/all_forums.html">Message Boards</a>
            </li>
        </ul>

    </div>
    <div class="menu">
        <h3>Tools &amp; Services</h3>
        <ul class="nav">
            <li>
                <a href="/wrap_external_link?external_url=https://businesscenter.osi.hu/login.aspx" target="_blank" title="Business Center">Business Center</a>
            </li>

            <li>
                <a href="/wrap_external_link?external_url=http://osi-ny.soros.org/troubletkt/step2.cfm?cat=Web" target="_blank" title="Request help with a website">Web Requests</a>
            </li>
            <li>
                <a href="http://snap.archivum.ws/dspace/community-list" target="_blank" title="Soros Network Archival Portal">SNAP</a>
            </li>
        </ul>
    </div>

    <div class="menu">
        <h3>Help Desk</h3>
        <ul class="nav">
            <li>
                <a href="/wrap_external_link?external_url=https://businesscenter.osi.hu/troubleticket/" target="_blank" title="Request technical assistance">Trouble Ticket </a>
            </li>
            <li>
                <a href="/offices/london/london-employee-resources/telephone-system-guide" title="Activate and manage you phone">Telephone System Guide</a>

            </li>
            <li>
                <a href="/offices/nyc/help-desk/login-problems/karl-user-name-and-password">KARL Login Help</a>
            </li>
            <li>
                <a href="/communities/about-karl/wiki/karl-user-manual" target="_blank" title="Help using KARL">KARL User Manual</a>
            </li>
        </ul>

    </div>
</div>
"""

nationalfoundation_navmenu = """<div>
    <div class="menu">
        <h3>About OSI</h3>

        <ul class="nav">
            <li>
                <a href="/offices/nyc/about-osi/about-osi-and-the-soros-foundations-network.html">About OSI &amp; Soros Foundations Network</a>
            </li>
            <li>
                <a href="/offices/nyc/about-osi/about-george-soros.html">About George Soros</a>
            </li>

            <li>
                <a href="/people/">Network Directory</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Resources</h3>
        <ul class="nav">

            <li>
                <a href="/offices/national-foundation/nf-resources/travel-authorization-and-security-policies">Travel Authorization and Security Policies</a>
            </li>
            <li>
                <a href="/offices/forums/all_forums.html">Message Boards</a>
            </li>
            <li>
                <a href="http://snap.archivum.ws/dspace/community-list" target="_blank" title="Soros Network Archival Portal">SNAP</a>

            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Help Desk</h3>
        <ul class="nav">
            <li>
                <a href="/offices/nyc/help-desk/login-problems/karl-user-name-and-password">KARL Login Help</a>

            </li>
            <li>
                <a href="/communities/about-karl/wiki/karl-user-manual">KARL User Manual</a>
            </li>
        </ul>
    </div>
</div>
"""

paris_navmenu = """<div>
    <div class="menu">
        <h3>About OSI</h3>

        <ul class="nav">
            <li>
                <a href="/offices/nyc/about-osi/about-osi-and-the-soros-foundations-network.html"
                    >About OSI &amp; Soros Foundations Network</a>
            </li>
            <li>
                <a href="/offices/nyc/about-osi/about-george-soros.html">About George Soros</a>
            </li>

            <li>
                <a href="/people/">Network Directory</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Resources</h3>
        <ul class="nav">

            <li>
                <a href="/offices/nyc/referencemanuals/travel-authorization-and-security-policies"
                    >Travel Authorization and Security Policies</a>
            </li>
            <li>
                <a href="/offices/forums/all_forums.html">Message Boards</a>
            </li>
        </ul>
    </div>

    <div class="menu">
        <h3>Tools &amp; Services</h3>
        <ul class="nav">
            <li>
                <a href="/wrap_external_link?external_url=https://businesscenter.osi.hu/login.aspx"
                    target="_blank" title="Business Center">Business Center</a>
            </li>
            <li>

                <a
                    href="/wrap_external_link?external_url=http://osi-ny.soros.org/troubletkt/step2.cfm?cat=Web"
                    target="_blank" title="Request help with a website">Web Requests</a>
            </li>
            <li>
                <a href="http://snap.archivum.ws/dspace/community-list" target="_blank"
                    title="Soros Network Archival Portal">SNAP</a>
            </li>
        </ul>
    </div>
    <div class="menu">

        <h3>Help Desk</h3>
        <ul class="nav">
            <li>
                <a href="/offices/nyc/help-desk/login-problems/karl-user-name-and-password">KARL
                    Login Help</a>
            </li>
            <li>
                <a href="/communities/about-karl/wiki/karl-user-manual">KARL User Manual</a>

            </li>
        </ul>
    </div>
</div>
"""

washington_navmenu = """<div>
    <div class="menu">
        <h3>About OSI</h3>

        <ul class="nav">
            <li>
                <a href="/offices/nyc/about-osi/about-osi-and-the-soros-foundations-network.html"
                    >About OSI &amp; Soros Foundations Network</a>
            </li>
            <li>
                <a href="/offices/nyc/about-osi/about-george-soros.html">About George Soros</a>
            </li>

            <li>
                <a href="/people/">Network Directory</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Resources</h3>
        <ul class="nav">

            <li class="submenu">
                <a href="/offices/nyc/referencemanuals">Administration</a>
                <ul class="level2">
                    <li>
                        <a href="/offices/nyc/referencemanuals/communications">Communications</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/facilities-management">Facilities
                            Management</a>

                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/finance">Finance</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/legal">Legal</a>
                    </li>
                    <li>

                        <a href="/offices/nyc/referencemanuals/grants-management">Grants
                            Management</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/human-resources">Human Resources</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/referencemanuals/information-systems">Information
                            Systems</a>

                    </li>
                    <li>
                        <a
                            href="/offices/nyc/referencemanuals/facilities-management/records-management-program"
                            >Records Management</a>
                    </li>
                    <li>
                        <a
                            href="/offices/nyc/referencemanuals/travel-authorization-and-security-policies"
                            >Travel Authorization and Security</a>
                    </li>
                    <li>

                        <a
                            href="/offices/nyc/referencemanuals/travel-expenses-guidelines-and-procedures"
                            >Travel and Expenses</a>
                    </li>
                </ul>
            </li>
            <li>
                <a href="/offices/forums/all_forums.html">Message Boards</a>
            </li>
        </ul>

    </div>
    <div class="menu">
        <h3>Tools &amp; Services</h3>
        <ul class="nav">
            <li>
                <a
                    href="/wrap_external_link?external_url=https://prs.soros.org/businesscenter/loginvalidate.aspx"
                    target="_blank" title="Business Center">Business Center</a>
            </li>

            <li class="submenu">
                <a
                    href="/wrap_external_link?external_url=http://osi-ny.soros.org/channel_select.cfm?Pulldown=Yes&amp;Channel=Events"
                    target="_blank" title="Reserve and view conference rooms in New York">NY Events
                    Calendar</a>
                <ul class="level2">
                    <li>
                        <a
                            href="/wrap_external_link?external_url=http://osi-ny.soros.org/events/step1.cfm?RequestType=ConferenceReservation"
                            target="_blank">Conference Room Reservation</a>
                    </li>
                    <li>
                        <a
                            href="/wrap_external_link?external_url=http://osi-ny.soros.org/events/at-a-glance.cfm?RequestType=MeetingPlanner"
                            target="_blank">Meeting Planner</a>

                    </li>
                </ul>
            </li>
            <li>
                <a
                    href="/wrap_external_link?external_url=http://osi-ny.soros.org/troubletkt/step2.cfm?cat=Web"
                    target="_blank" title="Request help with a website">Web Requests</a>
            </li>
            <li>
                <a
                    href="/wrap_external_link?external_url=http://osi-ny.soros.org/systems_hw_request/order/step1.cfm?RequestType=HardwareSoftwareRequest"
                    target="_blank" title="Request a new computer, monitor, or mouse"
                    >Hardware/Software Requests</a>

            </li>
            <li>
                <a
                    href="/wrap_external_link?external_url=https://prs.soros.org/travelrequest/loginvalidate.aspx"
                    target="_blank" title="Travel Requests">Travel Requests</a>
            </li>
            <li class="submenu">
                <a href="#" title="Research and Reference">Research &amp; Reference</a>
                <ul class="level2">

                    <li>
                        <a href="http://imgenie.soros.org/InmagicGenie/opac.aspx" target="_blank"
                            >Library Databases</a>
                    </li>
                    <li>
                        <a href="http://snap.archivum.ws/dspace/community-list" target="_blank"
                            title="Soros Network Archival Portal">SNAP</a>
                    </li>
                </ul>
            </li>

            <li>
                <a href="http://interactweb.soros.org/InterAction" target="_blank"
                    title="Find Contacts">Interaction</a>
            </li>
        </ul>
    </div>
    <div class="menu">
        <h3>Help Desk</h3>
        <ul class="nav">

            <li>
                <a
                    href="/wrap_external_link?external_url=http://osi-ny.soros.org/troubletkt/step1.cfm"
                    target="_blank" title="Request technical assistance">Trouble Ticket</a>
            </li>
            <li>
                <a href="/offices/nyc/help-desk/user-manuals/checking-webmail"
                    title="Checking your email via the web">Checking Webmail</a>
            </li>
            <li class="submenu">
                <a href="/offices/nyc/help-desk/more-systems-help">Login &amp; Password</a>

                <ul class="level2">
                    <li>
                        <a href="/offices/nyc/help-desk/more-systems-help/login-help">Login help</a>
                    </li>
                    <li>
                        <a href="/offices/nyc/help-desk/more-systems-help/changing-password"
                            >Changing Password</a>
                    </li>
                </ul>

            </li>
            <li>
                <a href="/communities/about-karl/wiki/karl-user-manual" target="_blank"
                    title="Help using KARL">Karl User Manual</a>
            </li>
        </ul>
    </div>
</div>
"""

paris_forums = [
    {'id': 'paris-personals', 'title': 'Paris Personals'},
    {'id': 'paris-news', 'title': 'Paris News'},
]

london_forums = [
    {'id': 'london-personals', 'title': 'London Personals'},
    {'id': 'london-news', 'title': 'London News'},
]

washington_forums = [
    {'id': 'washington-personals', 'title': 'Washington Personals'},
    {'id': 'washington-news', 'title': 'Washington News'},
]

brussels_forums = [
    {'id': 'brussels-personals', 'title': 'Brussels Personals'},
    {'id': 'brussels-news', 'title': 'Brussels News'},
]

baltimore_forums = [
    {'id': 'baltimore-personals', 'title': 'Baltimore Personals'},
    {'id': 'baltimore-news', 'title': 'Baltimore News'},
]

nationalfoundation_forums = [
    {'id': 'national-foundation-personals',
     'title': 'National Foundation Personals'},
    {'id': 'national-foundation-helpwanted',
     'title': 'National Foundation Help Wanted'},
    {'id': 'national-foundation-news',
     'title': 'National Foundation News',},
]

middle_portlets = ['/offices/files/network-news/',
                   '/offices/files/network-events/',
                   '/feeds/soros',
                   ]

class OSIOfficeData(object):
    implements(IInitialOfficeData)

    title = 'OSI'
    feature = sample_feature
    offices_acl = [
        (Allow, 'group.KarlAdmin', ADMINISTRATOR_PERMS),
        (Allow, 'group.KarlStaff', GUEST_PERMS),
        NO_INHERIT,
    ]

    offices = [
        {'id': 'nyc',
         'title': 'New York',
         'address': '400 West 59th Street',
         'city': 'New York',
         'state': 'NY',
         'country': 'U.S.A',
         'zipcode': '10019',
         'telephone': '1-212-548-0600',
         'middle_portlets': middle_portlets,
         'right_portlets': ['/offices/nyc/forums/nyc-news',
                            '/offices/nyc/forums/nyc-personals',
                           ],
         'forums': nyc_forums,
         'navmenu': nyc_navmenu,
         },
        {'id': 'baltimore',
         'title': 'Baltimore',
         'address': '201 North Charles Street Suite 1300',
         'city': 'Baltimore',
         'state': 'Maryland',
         'country': 'U.S.A.',
         'zipcode': '21201',
         'telephone': '1-410-234-1091',
         'middle_portlets': middle_portlets,
         'right_portlets': ['/offices/baltimore/forums/baltimore-news',
                            '/offices/baltimore/forums/baltimore-personals',
                           ],
         'forums': baltimore_forums,
         'navmenu': baltimore_navmenu,
         },
        {'id': 'budapest',
         'title': 'Budapest',
         'address': 'Oktober 6. u. 12.',
         'city': 'Budapest',
         'state': '',
         'country': 'Hungary',
         'zipcode': '',
         'telephone': '36-1-327-3100',
         'middle_portlets': middle_portlets,
         'right_portlets': ['/offices/budapest/forums/budapest-news',
                            '/offices/budapest/forums/budapest-personals',
                           ],
         'forums': budapest_forums,
         'navmenu': budapest_navmenu,
         },
        {'id': 'brussels',
         'title': 'Brussels',
         'address': '6 place Stephanie',
         'city': 'Brussels',
         'state': '',
         'country': 'Belgium',
         'zipcode': '',
         'telephone': '32-2-505-4646',
         'middle_portlets': middle_portlets,
         'right_portlets': ['/offices/brussels/forums/brussels-news',
                            '/offices/brussels/forums/brussels-personals',
                           ],
         'forums': brussels_forums,
         'navmenu': brussels_navmenu,
         },
        {'id': 'london',
         'title': 'London',
         'address': 'Cambridge House, 5th fl. 100 Cambridge Grove, Hammersmith',
         'city': 'London',
         'state': '',
         'country':
         'United Kingdom',
         'zipcode': 'W6 0LE',
         'telephone': '44-207-031-0200',
         'middle_portlets': middle_portlets,
         'right_portlets': ['/offices/london/forums/london-news',
                            '/offices/london/forums/london-personals',
                           ],
         'forums': london_forums,
         'navmenu': london_navmenu,
         },
        {'id': 'national-foundation',
         'title': 'National Foundation',
         'address': '',
         'city': '',
         'state': '',
         'country': '',
         'zipcode': '',
         'telephone': '',
         'middle_portlets': middle_portlets,
         'right_portlets': ['/offices/national-foundation/forums/' +
                                'national-foundation-helpwanted',
                            '/offices/national-foundation/forums/' +
                                 'national-foundation-personals',
                           ],
         'forums': nationalfoundation_forums,
         'navmenu': nationalfoundation_navmenu,
         },
        {'id': 'paris',
         'title': 'Paris',
         'address': '38 Boulevard Beaumarchais',
         'city': 'Paris',
         'state': '',
         'country': 'France',
         'zipcode': '',
         'telephone': '33-1-48-052-474',
         'middle_portlets': middle_portlets,
         'right_portlets': ['/offices/paris/forums/paris-news',
                            '/offices/paris/forums/paris-personals',
                           ],
         'forums': paris_forums,
         'navmenu': paris_navmenu,
         },
        {'id': 'washington',
         'title': 'Washington',
         'address': '1120 19th Street NW, 8th Fl.',
         'city': 'Washington',
         'state': 'DC',
         'country': 'U.S.A.',
         'zipcode': '20036',
         'telephone': '1-202-721-5600',
         'middle_portlets': middle_portlets,
         'right_portlets': ['/offices/washington/forums/washington-news',
                            '/offices/washington/forums/washington-personals',
                           ],
         'forums': washington_forums,
         'navmenu': washington_navmenu,
         },
    ]

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
