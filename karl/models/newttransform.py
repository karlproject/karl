import json
import zlib

def transform(class_name, state):
    if class_name == 'karl.content.models.adapters._CachedData':
        state = json.loads(state)
        text = zlib.decompress(state['data']['hex'].decode('hex'))
        try:
            text = text.decode(
                state.get('encoding', 'ascii')).replace('\x00', '')
        except UnicodeDecodeError:
            text = ''

        return json.dumps(dict(text=text))
