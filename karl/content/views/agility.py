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

from repoze.bfg.chameleon_zpt import render_template_to_response
from repoze.bfg.url import model_url

from karl.views.api import TemplateAPI

from karl.views.utils import convert_to_script

from karl.content.views.atom import WikiAtomFeed

def get_agility_data(context, request):

    response = {
        "items": [],
        "timeslots": {
                    "0": "January 1",
                    "1": "January 8",
                    "2": "February 1"
                }
    }
    entries = WikiAtomFeed(context, request)._entry_models
    counter = 0
    for entry in entries:
        counter = counter + 1
        item = {
                                "id": "id_" + str(counter),
                                "num": counter,
                                "timeslot": 0,
                                "title": entry.title,
                                "who": "Paul"
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

_sample_data = {"items":
                    [
                                {
                                "id": "id_0",
                                "num": 0,
                                "timeslot": 0,
                                "title": "Task 0",
                                "who": "Paul"
                            },
                                {
                                    "id": "id_1",
                                    "num": 1,
                                    "timeslot": 1,
                                    "title": "Task 1",
                                    "who": "Chris"
                                },
                                {
                                    "id": "id_2",
                                    "num": 2,
                                    "timeslot": 2,
                                    "title": "Task 2",
                                    "who": "Robert"
                                },
                                {
                                    "id": "id_3",
                                    "num": 3,
                                    "timeslot": 0,
                                    "title": "Task 3",
                                    "who": "Paul"
                                },
                                {
                                    "id": "id_4",
                                    "num": 4,
                                    "timeslot": 0,
                                    "title": "Simply Task 4",
                                    "who": "Robert"
                                },
                                {
                                    "id": "id_5",
                                    "num": 5,
                                    "timeslot": 0,
                                    "title": "Another Task 5",
                                    "who": "Chris"
                                }

                    ],
                "timeslots": {
                    "0": "January 1",
                    "1": "January 8",
                    "2": "February 1"
                }
}