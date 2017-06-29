# Extract GSA category info from the "full" GSA sync XML.
import sys

from lxml.etree import parse


def _text(node, sub):
    children = node.xpath('./%s' % sub)
    if children:
        text = children[0].text
        if text is not None:
            return text.encode('utf8')


def make_adr(node):
    return {'street_address': _text(node, 'street-address'),
            'extended_address': _text(node, 'extended-address'),
            'locality': _text(node, 'locality'),
            'region': _text(node, 'region'),
            'postal_code': _text(node, 'postal-code'),
            'country_name': _text(node, 'country-name'),
           }


def make_tel(node):
    return {'type': node.get('type'),
            'number': node.text,
           }


def make_email(node):
    return {'type': node.get('type'),
            'address': node.text,
           }


def make_hcard(node):
    info = {'fn': _text(node, 'fn'),
            'org': _text(node, 'org'),
            'url': _text(node, 'url'),
            'note': _text(node, 'note'),
           }
    adrs = info['adrs'] = []
    for sub in node.xpath('./adrs/adr'):
        adrs.append(make_adr(sub))
    tels = info['tels'] = []
    for sub in node.xpath('./tels/tel'):
        tels.append(make_tel(sub))
    emails = info['emails'] = []
    for sub in node.xpath('./emails/email'):
        emails.append(make_email(sub))
    return info


_DE_PLURALIZE = {
    'departments': 'Department',
    'entities': 'Entity',
    'offices': 'Office',
}

def make_item(node, category):
    info = {'title': _text(node, 'title'),
            'category': _DE_PLURALIZE[category],
           }
    hcard = node.xpath('./hcard')
    if hcard:
        info['hcard'] = make_hcard(hcard[0])
    return info

def extract_categories(stream):
    tree = parse(stream)
    by_id = {}
    by_category = {}
    for item in tree.xpath('//category_item'):
        c_id = int(_text(item, 'id'))
        p_type = item.xpath('..')[0].get('id')
        if c_id not in by_id:
            by_id[c_id] = make_item(item,  p_type)
        ids_by_type = by_category.get(p_type)
        if ids_by_type is None:
            ids_by_type = by_category[p_type] = set()
        ids_by_type.add(c_id)
    return by_id, by_category


def main(argv=sys.argv):
    by_id, by_category = extract_categories(open(argv[1]))

    for name, ids in sorted(by_category.items()):
        for id in ids:
            info = by_id[id]
            print '-' * 80
            print '%09d %s (%s)' % (id, info['title'], info['category'].lower())
            print '-' * 80
            hcard = info['hcard'] 
            for adr in hcard['adrs']:
                print 'Address : %s' % adr['street_address']
                if adr['extended_address']:
                    print '          %s' % adr['extended_address']
                print '          %s, %s %s' % (adr['locality'],
                                               adr['region'],
                                               adr['postal_code'])
                print '          %s' % adr['country_name']
            for tel in hcard['tels']:
                print '%-8s: %s' % (tel['type'], tel['number'])
            for email in hcard['emails']:
                print '%-8s: %s' % (email['type'], email['address'])
            print


if __name__ == '__main__':
    main()
