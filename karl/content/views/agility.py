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

import json
from random import choice

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.url import model_url

from karl.views.api import TemplateAPI

from karl.views.utils import convert_to_script

from karl.content.views.atom import WikiAtomFeed

_sample_eval_dates = ["07-Jun", "14-Jun", "21-Jun", "28-Jun"]
_sample_sows = ["35", "36", "37"]
_sample_benefits = ["First Benefit", "Another good reason", "Slam Dunk"]
_sample_descriptions = [
        "This project is neat.  It has text that might span multiple lines",
        "Another project is neat.  It has text spans multiple lines",
        "My project is great.  It has text that might span multiple lines",
        ]

def set_agility_data(context, request):
    item = json.loads(request.body)

    context[item['name']].title = item['title']

    return 99

def get_agility_data(context, request):

    response = {
        "items": [],
        "sows": {
            "35": "SOW35: May-Jul 2011",
            "36": "SOW36: Aug-Sep 2011",
            "37": "SOW37: Oct-Nov 2011"
        }
    }
    entries = WikiAtomFeed(context, request)._entry_models
    counter = 0
    for entry in entries:
        counter = counter + 1
        this_eval_date = choice(_sample_eval_dates)
        this_sow = choice(_sample_sows)
        this_desc = choice(_sample_descriptions)
        item = {
                                "id": "id_" + str(counter),
                                "name": entry.__name__,
                                "num": counter,
                                "sow": this_sow,
                                "title": entry.title,
                                "who": "Paul",
                                "benefits": _sample_benefits,
                                "description": this_desc,
                                "eval_date": this_eval_date
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
        wiki_url = backto["href"]
    ))

    feed_url = model_url(context, request, "atom.xml")
    return render_template_to_response(
        'templates/show_agility.pt',
        api=api,
        head_data=client_json_data,
        backto=backto,
        )
