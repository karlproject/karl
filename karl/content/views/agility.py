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

import simplejson as json
from random import choice

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.url import model_url

from karl.views.api import TemplateAPI

from karl.views.utils import convert_to_script

from karl.content.views.atom import WikiAtomFeed

def get_agility_config(wiki):
    """At some point this will be persistent"""
    vocabularies = {
        "category": {
            "0": "Search",
            "1": "Files",
            "2": "Hosting",
            "3": "Versioning"
        },
        "sow": {
            "35": "SOW35: May-Jul 2011",
            "36": "SOW36: Aug-Sep 2011",
            "37": "SOW37: Oct-Nov 2011",
            "999": "Not Assigned"
        }
    }
    config = {
        'vocabularies': vocabularies,
        'group_by': "category"}

    return config


def set_agility_data(context, request):
    item = json.loads(request.body)

    context[item['name']].title = item['title']
    context[item['name']].agility = item
    print item
    print "Saved"
    return 99


def get_agility_data(context, request):
    response = {
        "items": [],
        "config": get_agility_config(None),
        }
    entries = WikiAtomFeed(context, request)._entry_models
    for entry in entries:
        # For now, if data haven't been assigned yet to the .agility
        # JSON pile, make up some values for the purposes of testing.
        this_desc = "No description."
        this_eval_date = "None"
        this_sow = "999"
        this_benefits = ["No Benefits Listed", ]
        this_category = 0
        this_estimated = 1.4
        if hasattr(entry, "agility"):
            this_desc = entry.agility["description"]
            this_eval_date = entry.agility["eval_date"]
            this_sow = entry.agility["sow"]
            this_benefits = entry.agility["benefits"]
            this_category = entry.agility.get("category", 0)
        item = {
            "id": "id_" + entry.__name__,
            "name": entry.__name__,
            "sow": this_sow,
            "title": entry.title,
            "who": "Paul",
            "benefits": this_benefits,
            "description": this_desc,
            "eval_date": this_eval_date,
            "category": this_category,
            "estimated": this_estimated
        }

        response["items"].append(item)

    return response


def show_agility_view(context, request):
    backto = {
        'href': model_url(context, request),
        'title': context.title,
        }

    api = TemplateAPI(context, request, "Agility")

    client_json_data = convert_to_script(dict(
        wiki_url=backto["href"]
    ))

    feed_url = model_url(context, request, "atom.xml")
    return render_template_to_response(
        'templates/show_agility2.pt',
        api=api,
        head_data=client_json_data,
        backto=backto,
        )
