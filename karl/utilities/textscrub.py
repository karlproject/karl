import re
import markdown2

REPLY_SEPARATOR = re.compile("--- Reply ABOVE THIS LINE to post a comment ---")
_OUTLOOK = re.compile(r'[>|\s]*-----\s?Original Message\s?-----')
_OUTLOOK_EXPRESS = re.compile(r'________________________________')
_GMAIL = re.compile(r'\nOn (Mon|Tue|Wed|Thu|Fri|Sat|Sun), (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Nov|Oct|Dec) \d{1,2}')
_THUNDERBIRD = re.compile(r'\n[^\n]*wrote:\n>')

cutoffs = [
    REPLY_SEPARATOR,
    _OUTLOOK,
    _OUTLOOK_EXPRESS,
    _GMAIL,
    _THUNDERBIRD
]

# Convert urls found in mailin text into links using the markdown syntax.
url_re = re.compile('http(s)?:[^\s]+')
def url_to_markdown_link(match):
    url = match.group()
    title = url.replace('_', '\_')
    return '[%s](%s)' % (title, url)

def text_scrubber(text, mimetype=None):
    # We're assuming plain text
    if mimetype is not None and mimetype != "text/plain":
        raise Exception("Unsupported mime type: %s" % mimetype)

    for pattern in cutoffs:
        match = pattern.search(text)
        if match:
            text = text[:match.start()].strip()

    text = url_re.sub(url_to_markdown_link, text)
    return markdown2.markdown(text)
