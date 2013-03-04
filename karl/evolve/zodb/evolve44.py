from karl.models.contentfeeds import APPENDSTACK_MAX_LAYERS
from karl.models.contentfeeds import APPENDSTACK_MAX_LENGTH

def evolve(context):
    events = getattr(context, 'events')
    if events._max_layers != APPENDSTACK_MAX_LAYERS:
        print "Update 'events' from %d to %d layers" % (
             events._max_layers, APPENDSTACK_MAX_LAYERS)
        events._max_layers = APPENDSTACK_MAX_LAYERS
    if events._max_length != APPENDSTACK_MAX_LENGTH:
        print "Update 'events' from %d to %d items per layer" % (
             events._max_length, APPENDSTACK_MAX_LENGTH)
        events._max_length = APPENDSTACK_MAX_LENGTH
