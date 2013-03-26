from karl.models.contentfeeds import APPENDSTACK_MAX_LAYERS
from karl.models.contentfeeds import APPENDSTACK_MAX_LENGTH

def evolve(context):
    events = getattr(context, 'events')
    stack = events._stack
    if stack._max_layers != APPENDSTACK_MAX_LAYERS:
        print "Update 'events._stack' from %d to %d layers" % (
             stack._max_layers, APPENDSTACK_MAX_LAYERS)
        stack._max_layers = APPENDSTACK_MAX_LAYERS
    if stack._max_length != APPENDSTACK_MAX_LENGTH:
        print "Update 'events._stack' from %d to %d items per layer" % (
             stack._max_length, APPENDSTACK_MAX_LENGTH)
        stack._max_length = APPENDSTACK_MAX_LENGTH
