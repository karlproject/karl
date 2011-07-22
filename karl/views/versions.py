import datetime

from webob.exc import HTTPFound
from repoze.bfg.url import model_url
from sqlalchemy.orm.exc import NoResultFound

from karl.utils import find_repo
from karl.utils import find_profiles
from karl.views.api import TemplateAPI


def show_history(context, request):
    repo = find_repo(context)
    profiles = find_profiles(context)

    def display_record(record):
        editor = profiles[record.user]
        return {
            'date': format_local_date(record.archive_time),
            'editor': {
                'name': editor.title,
                'url': model_url(editor, request),
                },
            'preview_url': '#',
            'restore_url': model_url(
                context, request, 'revert',
                query={'version_num': str(record.version_num)}),
            'is_current': record.current_version == record.version_num,
        }

    try:
        history = map(display_record, repo.history(context.docid))
        history.reverse()
    except:
        history = []
    page_title = 'History for %s' % context.title
    return {
        'api': TemplateAPI(context, request, page_title),
        'history': history,
    }


def revert(context, request):
    repo = find_repo(context)
    version_num = int(request.params['version_num'])
    for version in repo.history(context.docid):
        if version.version_num == version_num:
            break
    else:
        raise ValueError('No such version: %d' % version_num)
    context.revert(version)
    repo.reverted(context.docid, version_num)
    return HTTPFound(location=model_url(context, request))


def format_local_date(date):
    return date.strftime('%Y-%m-%d %H:%M')
