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

_LOOKUP = {
    'application/msword': {
        'small_icon_name': 'doc_small.gif',
        'large_icon_name': 'doc_big.gif',
        'title': 'Word'
        },
    'application/pdf': {
        'small_icon_name': 'pdf_small.gif',
        'large_icon_name': 'pdf_big.gif',
        'title': 'PDF'
        },
    'application/vnd.ms-excel': {
        'small_icon_name': 'xls_small.gif',
        'large_icon_name': 'xls_big.gif',
        'title': 'Excel'
        },
    'application/vnd.ms-powerpoint': {
        'small_icon_name': 'ppt_small.gif', 
        'large_icon_name': 'ppt_big.gif',
        'title': 'PowerPoint'
        },
    'audio/mpeg': {
        'small_icon_name': 'mp3_small.gif', 
        'large_icon_name': 'mp3_big.gif', 
        'title': 'MP3'
        },
    'image/gif': {
        'small_icon_name': 'gif_small.gif',
        'large_icon_name': 'gif_big.gif',
        'title': 'GIF Image'
        },
    'image/jpeg': {
        'small_icon_name': 'jpg_small.gif', 
        'large_icon_name': 'jpg_big.gif',
        'title': 'JPEG Image'
        },
    'image/png': {
        'small_icon_name': 'png_small.gif', 
        'large_icon_name': 'png_big.gif',
        'title': 'PNG Image'
        },
    'text/plain': {
        'small_icon_name': 'txt_small.gif', 
        'large_icon_name': 'txt_big.gif',
        'title': 'Text File'
        },
    'text/html': {
        'small_icon_name': 'html_small.gif', 
        'large_icon_name': 'html_big.gif',
        'title': 'HTML File'},
    }

def mime_info(mime_type):
    info = _LOOKUP.get(mime_type)
    if info is None:
        if '/' in mime_type:
            title = mime_type.split('/', 1)[1].capitalize()
        else:
            title = 'Generic File'

        info = {
            'small_icon_name': 'mime.png',
            'large_icon_name': 'mime.png',
            'title':title
        }

    return info
