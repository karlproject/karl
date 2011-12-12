from karl.views.communities import show_active_communities_view
from karl.views.community import show_community_view

def global_nav(context, request):
    return request.get('karl_view_data', {})

def personal_tools(context, request):
    return request.get('karl_view_data', {})

def search(context, request):
    return request.get('karl_view_data', {})

def context_tools(context, request):
    return request.get('karl_view_data', {})

def actions_menu(context, request):
    return request.get('karl_view_data', {})

def column_one(context, request):
    return request.get('karl_view_data', {})

def communities(context, request):
    view_data = show_active_communities_view(context, request)   
    request['karl_view_data'] = view_data
    return view_data

def community(context, request):
    view_data = show_community_view(context, request)   
    request['karl_view_data'] = view_data
    return view_data

