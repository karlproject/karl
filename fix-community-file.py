import newt.db.search
import karl.content.models.adapters
from ZODB.utils import u64

obs = newt.db.search.where(
    root._p_jar,
    "class_name = 'karl.content.models.files.CommunityFile' and"
    " not (state ? '_extracted_data')")
for ob in obs:
    karl.content.models.adapters._extract_and_cache_file_data(ob)
    root._p_jar.transaction_manager.commit()
    #print u64(ob._p_oid)
