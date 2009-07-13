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

"""Useful functions that appear in several places in the KARL UI"""
import os
import re
from cStringIO import StringIO

from repoze.bfg.security import authenticated_userid
from repoze.bfg.traversal import traverse
from repoze.lemonade.content import create_content

from formencode import Invalid

from karl.utils import find_communities
from karl.utils import find_profiles
from karl.utils import find_site
from karl.utils import find_users
from karl.utils import get_setting

from karl.models.interfaces import IImageFile
from karl.models.image import mimetypes as image_mimetypes

from simplejson import JSONEncoder
from textwrap import dedent
from PIL import Image

_convert_to_dashes = re.compile(r"""[\s/:"']""") # ' damn you emacs
_safe_char_check = re.compile(r"[\w.-]+$")
_reduce_dashes = re.compile(r"-{2,}")

_ascii_mapping = {
    # This is pulled from plone.i18n.normalizer.  It is a partial mapping
    # of Unicode characters that look similar to ASCII letters.  Non-ASCII
    # characters not listed here will be encoded in hexadecimal.

    # Latin characters with accents, etc.
    138 : 's', 140 : 'O', 142 : 'z', 154 : 's', 156 : 'o', 158 : 'z',
    159 : 'Y', 192 : 'A', 193 : 'A', 194 : 'A', 195 : 'a', 196 : 'AE',
    197 : 'Aa', 198 : 'AE', 199 : 'C', 200 : 'E', 201 : 'E', 202 : 'E',
    203 : 'E', 204 : 'I', 205 : 'I', 206 : 'I', 207 : 'I', 208 : 'Th',
    209 : 'N', 210 : 'O', 211 : 'O', 212 : 'O', 213 : 'O', 214 : 'OE',
    215 : 'x', 216 : 'O', 217 : 'U', 218 : 'U', 219 : 'U', 220 : 'UE',
    222 : 'th', 221 : 'Y', 223 : 'ss', 224 : 'a', 225 : 'a', 226 : 'a',
    227 : 'a', 228 : 'ae', 229 : 'aa', 230 : 'ae', 231 : 'c',
    232 : 'e', 233 : 'e', 234 : 'e', 235 : 'e', 236 : 'i', 237 : 'i',
    238 : 'i', 239 : 'i', 240 : 'th', 241 : 'n', 242 : 'o', 243 : 'o',
    244 : 'o', 245 : 'o', 246 : 'oe', 248 : 'oe', 249 : 'u', 250 : 'u',
    251 : 'u', 252 : 'ue', 253 : 'y', 254 : 'Th', 255 : 'y' ,
    # Turkish
    286 : 'G', 287 : 'g', 304 : 'I', 305 : 'i', 350 : 'S', 351 : 's',
    # Polish
    321 : 'L', 322 : 'l',
    # French
    339: 'oe',
    # Greek
    902: 'A', 904: 'E', 905: 'H', 906: 'I', 908: 'O', 910: 'Y', 911: 'O',
    912: 'i', 913: 'A', 914: 'B', 915: 'G', 916: 'D', 917: 'E', 918: 'Z',
    919: 'I', 920: 'Th', 921: 'I', 922: 'K', 923: 'L', 924: 'M', 925: 'N',
    926: 'Ks', 927: 'O', 928: 'P', 929: 'R', 931: 'S', 932: 'T', 933: 'Y',
    934: 'F', 935: 'Ch', 936: 'Ps', 937: 'O', 938: 'I', 939: 'Y', 940: 'a',
    941: 'e', 942: 'i', 943: 'i', 944: 'y', 945: 'a', 946: 'b', 947: 'g',
    948: 'd', 949: 'e', 950: 'z', 951: 'i', 952: 'th', 953: 'i', 954: 'k',
    955: 'l', 956: 'm', 957: 'n', 958: 'ks', 959: 'o', 960: 'p', 961: 'r',
    962: 's', 963: 's', 964: 't', 965: 'y', 966: 'f', 967:'ch', 968: 'ps',
    969: 'o', 970: 'i', 971: 'y', 972: 'o', 973: 'y', 974: 'o',
    # Russian
    1081 : 'i', 1049 : 'I', 1094 : 'c', 1062 : 'C',
    1091 : 'u', 1059 : 'U', 1082 : 'k', 1050 : 'K',
    1077 : 'e', 1045 : 'E', 1085 : 'n', 1053 : 'N',
    1075 : 'g', 1043 : 'G', 1096 : 'sh', 1064 : 'SH',
    1097 : 'sch', 1065 : 'SCH', 1079 : 'z', 1047 : 'Z',
    1093 : 'h', 1061 : 'H', 1098 : '', 1066 : '',
    1092 : 'f', 1060 : 'F', 1099 : 'y', 1067 : 'Y',
    1074 : 'v', 1042 : 'V', 1072 : 'a', 1040 : 'A',
    1087 : 'p', 1055 : 'P', 1088 : 'r', 1056 : 'R',
    1086 : 'o', 1054 : 'O', 1083 : 'l', 1051 : 'L',
    1076 : 'd', 1044 : 'D', 1078 : 'zh', 1046 : 'ZH',
    1101 : 'e', 1069 : 'E', 1103 : 'ya', 1071 : 'YA',
    1095 : 'ch', 1063 : 'CH', 1089 : 's', 1057 : 'S',
    1084 : 'm', 1052 : 'M', 1080 : 'i', 1048 : 'I',
    1090 : 't', 1058 : 'T', 1100 : '', 1068 : '',
    1073 : 'b', 1041 : 'B', 1102 : 'yu', 1070 : 'YU',
    1105 : 'yo', 1025 : 'YO',
}

def _encode_name(name):
    """Encode the Unicode characters in a name"""
    res = []
    for c in name:
        if _safe_char_check.match(c):
            res.append(c)
            continue
        n = ord(c)
        if n < 128:
            # Discard ASCII symbols like '?', '$', etc.
            continue
        encoded = _ascii_mapping.get(n)
        if not encoded:
            encoded = '-%x-' % n
        res.append(encoded)
    return ''.join(res)


def make_name(context, title, raise_error=True):
    """Make a correct __name__ that is unique in the context"""

    name = title.lower()
    name = _convert_to_dashes.sub("-", name)
    if not _safe_char_check.match(name):
        name = _encode_name(name)
    name = _reduce_dashes.sub("-", name)

    if not name and raise_error:
        raise ValueError('The name must not be empty')

    # Make sure the name is unique in the context
    if name in context and raise_error:
        fmt = "The name '%s' already exists in folder '%s'"
        msg = fmt % (name, context.__name__)
        raise ValueError(msg)
    else:
        return name

def make_unique_name(context, title):
    """Make a correct __name__ that is unique in the context.
    
    Try until an empty name is found (or be debunked by a
    conflict error).
    """
    postfix = ''
    counter = 1
    while True:    
        try:
            return make_name(context, title + postfix)
        except ValueError:
            postfix = '-%i' % (counter, )
            counter += 1
            # This could actually cause all our
            # processes hang forever :)


def basename_of_filepath(title):
    """
    At least on Windows under IE, title holds the full path, e.g.::
    
       /communities/test1/files/c:\Documents and Settings\admin\Desktop\somefile.doc
    
    We need to just get the last part.

    usage::

        make_name(context, basename_of_filepath(title))
        make_unique_name(context, basename_of_filepath(title))

    """
    return title.rsplit("\\", 1)[-1]


def convert_to_script(data):
    if data:
        ##print data
        result = JSONEncoder().encode(data)
        script = dedent("""\
            <script type="text/javascript">
            window.karl_client_data = %s;
            </script>""" % (result, ))
    else:
        # no data, no script.
        script = ''
    return script


def _concat_path(fname, *rnames):
    return os.path.join(os.path.dirname(fname), *rnames)

def local_path(*rnames):
    return _concat_path(__file__, *rnames)

templates_formfields_path = local_path('templates', 'formfields.pt')

def _get_user_home_path(context, request):
    """If currently authenticated user has a 'home_path' set, create a response
    redirecting user to that path.  Otherwise return None.
    """
    userid = authenticated_userid(request)
    if userid is None:
        return None, None
    
    site = find_site(context)
    profiles = find_profiles(site)
    profile =  profiles.get(userid, None)
    if profile is None:
        return None, None
    
    home_path = getattr(profile, 'home_path', None)
    if home_path:
        # OSI sets this to a single space to mean None
        home_path = home_path.strip()
    if not home_path:
        return None, None
        
    tdict = traverse(site, home_path)
    target = tdict['context']
    view_name = tdict['view_name']
    subpath = tdict['subpath']
    
    if view_name:
        subpath.insert(0, view_name)
    
    return target, subpath

def get_user_community_names(context, request):
    userid = authenticated_userid(request)
    if userid is None:
        return []
    
    users = find_users(context)
    user = users.get_by_id(userid)
    community_names = set()
    for group in user["groups"]:
        if group.startswith("group.community:"):
            community_names.add(group.split(":")[1])

    return community_names

def get_user_home(context, request):
    # Respect user's home_path, if set
    home, extra_path = _get_user_home_path(context, request)
    if home is not None:
        return home, extra_path
    
    # If user is member of only one community, home is that community
    communities = find_communities(context)
    community_names = get_user_community_names(context, request)
    if len(community_names) == 1:
        community = communities.get(community_names.pop(), None)
        if community is not None:
            return community, []
            
    return communities, []
    
def handle_photo_upload(context, form, thumbnail=False):
    upload = form.get("photo", None)
    if upload is not None:
        upload_file = upload.file
        upload_type = upload.type
        assert upload_type

        if thumbnail:
            if not hasattr(upload_file, 'seek'):
                upload_file = StringIO(upload_file.read())

            # save the source photo (in case we later decide to use
            # a different thumbnail size)
            source_photo = create_content(IImageFile, upload_file, upload_type)
            upload_file.seek(0)

            # make the thumbnail
            try:
                upload_file, upload_type = make_thumbnail(
                    upload_file, upload_type)
            except IOError, e:
                raise CustomInvalid({"photo": str(e)})

            if 'source_photo' in context:
                del context['source_photo']
            context['source_photo'] = source_photo

        photo = context.get_photo()
        if photo is None:
            photo = create_content(
                IImageFile,
                upload_file,
                upload_type
            )
            name = "photo.%s" % photo.extension
            context[name] = photo

        else:
            if photo.mimetype != upload_type:
                del context[photo.__name__]
                photo.mimetype = upload_type
                name = "photo.%s" % photo.extension
                context[name] = photo
            photo.upload(upload_file)
        check_upload_size(context, photo, 'photo')

    # Handle delete photo (ignore if photo also uploaded)
    elif form.get("photo_delete", False):
        photo = context.get_photo()
        if photo is not None:
            del context[photo.__name__]

def make_thumbnail(upload_file, upload_type, max_width=75, max_height=100):
    img = Image.open(upload_file)
    width, height = img.size

    if (width == max_width and
            height == max_height and
            upload_type in image_mimetypes):
        # already the right size and format
        upload_file.seek(0)
        return upload_file, upload_type

    # scale
    image_ratio = float(width) / float(height)
    container_ratio = float(max_width) / float(max_height)
    if image_ratio >= container_ratio:
        # wide image
        width = int(max_height * image_ratio)
        height = max_height
    else:
        # tall image
        width = max_width
        height = int(max_width / image_ratio)
    img = img.resize((width, height), Image.ANTIALIAS)

    # crop
    if width > max_width:
        margin = (width - max_width) / 2
        img = img.crop((margin, 0, margin + max_width, height))
        width = max_width
    if height > max_height:
        margin = (height - max_height) / 2
        img = img.crop((0, margin, width, margin + max_height))
        height = max_height

    upload_file = StringIO()
    img.save(upload_file, 'JPEG', quality=90)
    upload_file.seek(0)
    upload_type = 'image/jpeg'
    return upload_file, upload_type

class CustomInvalid(Invalid):

    def __init__(self, error_dict):
        self.error_dict = error_dict

def check_upload_size(context, obj, field_name):
    max_size = int(get_setting(context, 'upload_limit', 0))
    if max_size and obj.size > max_size:
        msg = 'File size exceeds KARL upload limit of %d.' % max_size
        raise CustomInvalid({field_name: msg})
