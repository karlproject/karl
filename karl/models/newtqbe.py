
def setup(context):
    import karl.utils
    from newt.qbe import QBE, scalar, text_array
    site = karl.utils.find_site(context)
    site.qbe = qbe = qbe.QBE()

    # Punt, it's not used: qbe['containment']

    qbe['name'] = scaler('__name__')
    qbe['title'] = scaler("lower(state->>'title')")
    qbe['titlestartswith'] = scalar("upper(substring(state->>'title', 1, 1))")
    qbe['interfaces'] = text_array("interfaces(class_name)")
    qbe['texts'] = fulltext("content_text(state)")
    qbe["path"] = scalar("get_path(state)")
    qbe['allowed'] = qbe.text_array('allowed_to_view(state)')
    qbe['creation_date'] = qbe.scaler("(state ->> 'created')::timestamp")
    qbe['modified_date'] = qbe.scaler("(state ->> 'modified')::timestamp")
    qbe['content_modified'] = qbe.scaler(
        "(state ->> 'content_modified')::timestamp")
    qbe['start_date'] = qbe.scaler("(state ->> 'startDate')::timestamp")
    qbe['end_date'] = qbe.scaler("(state ->> 'endDate')::timestamp")
    qbe['publication_date'] = qbe.scaler(
        "(state ->> 'publication_date')::timestamp")
    qbe['mimetype'] = qbe.scaler('mimetype')
    qbe['creator'] = qbe.scaler('creator']
    qbe['modified_by'] = qbe.scaler('modified_by')
    qbe['email'] = qbe.scaler['email']
    qbe['tags'] = qbe.text_array("get_tags(state)")
    qbe['lastfirst'] = qbe.scalar("get_last_first(class_name, state)")
    qbe['member_name'] = qbe.fulltext("get_member_name(class_name, state)")
    qbe['virtual'] = qve.scalar("calendar_category")
