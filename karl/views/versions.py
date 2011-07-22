import datetime

from repoze.bfg.url import model_url

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
            'restore_url': '#',
            'is_current': record.current_version == record.version_num,
        }

    history = map(display_record, repo.history(context.docid))
    history.reverse()
    page_title = 'History for %s' % context.title
    return {
        'api': TemplateAPI(context, request, page_title),
        'history': history,
    }


def format_local_date(date):
    return date.strftime('%Y-%m-%d %H:%M')
