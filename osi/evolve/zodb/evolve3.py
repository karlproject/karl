from karl.security.workflow import reset_security_workflow
from pyramid.traversal import traverse
from pyramid.traversal import model_path

exceptions = [
    '/communities/about-karl',
    '/offices/baltimore',
    '/offices/brussels/annual-strategy',
    '/offices/brussels/brussels-employee-resources/holiday-schedule',
    '/offices/brussels/papers-articles-speeches',
    '/offices/brussels/referencemanuals/human-resources',
    '/offices/brussels/referencemanuals',
    '/offices/budapest/referencemanuals/human-resources',
    '/offices/budapest/referencemanuals/office-management',
    '/offices/budapest/referencemanuals/records-management',
    '/offices/budapest',
    '/offices/files/feature-graphics',
    '/offices/files/network-events',
    '/offices/files/network-news',
    '/offices/london/referencemanuals/human-resources',
    '/offices/london',
    '/offices/london',
    '/offices/national-foundation/nf-resources',
    '/offices/nyc/nyc-employee-resources/employee_handbook_2007.pdf',
    '/offices/nyc/nyc-employee-resources',
    '/offices/nyc/office-events',
    '/offices/nyc/referencemanuals/communications',
    '/offices/nyc/referencemanuals/facilities-management',
    '/offices/nyc/referencemanuals/finance',
    '/offices/nyc/referencemanuals/grants-management',
    '/offices/nyc/referencemanuals/human-resources',
    '/offices/nyc/referencemanuals/records-management',
    '/offices/nyc/referencemanuals/travel-authorization-and-security-policies',
    '/offices/nyc/referencemanuals/travel-expenses-guidelines-and-procedures',
    '/offices/nyc/whats-for-lunch',
    '/offices/washington',
    '/offices',
    ]

def evolve(context):
    for path in exceptions:
        d = traverse(context, path)
        ob = d['context']
        if model_path(ob) == path:
            if hasattr(ob, '__acl__'):
                ob.__custom_acl__ = ob.__acl__
    reset_security_workflow(context)
