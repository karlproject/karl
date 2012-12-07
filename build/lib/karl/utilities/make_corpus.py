
"""Create a simulated document corpus based on wonderland.txt."""

import os
import random
import re

here = os.path.dirname(__file__)
source = open(os.path.join(here, 'wonderland.txt')).read()

cap_words = list(set(re.findall(r'\b[A-Z][a-z]+\b', source)))
text_words = re.findall(r"\b[a-z]{2,20}\b", source)

print 'drop table if exists corpus;'

print 'CREATE TABLE corpus (id INT primary key, title TEXT, body TEXT,'
print '    all_vec TSVECTOR, all_but_body_vec TSVECTOR);'

print 'COPY corpus (id, title, body) FROM STDIN;'

for i in range(int(1e5)):
    title_length = range(random.randint(2, 5))
    title = ' '.join(random.choice(cap_words) for _ in title_length)
    index = random.randint(0, len(text_words))
    length = random.randint(100, 10000)
    body = ' '.join(text_words[index:index + length])
    print "%d\t%s\t%s" % (i + 1, title, body)

print r'\.'
