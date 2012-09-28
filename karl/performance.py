import inspect
import sys
import time

"""
Instrument the stack to make timing measurements.  This has a major drag on
performance.  Never, ever use in production.
"""

class timetrace(object):
    inner = False

    def __init__(self, threshold):
        self.threshold = threshold
        self.frame_node = FrameNode(None, None)
        self.finished = False

    def __enter__(self):
        self.savetrace = prev = sys.gettrace()
        if isinstance(prev, notrace) and isinstance(prev.prev, timetrace):
            self.inner = True
            self.frame_node = prev.prev.frame_node
        else:
            self.frame_node = FrameNode(None, None)
        sys.settrace(self)

    def __call__(self, frame, event, arg):
        assert event == 'call'
        if self.finished:
            return
        info = inspect.getframeinfo(frame)
        self.frame_node = FrameNode(info, self.frame_node)
        def inner_trace(innerframe, event, arg):
            assert innerframe is frame
            if event == 'return':
                self.frame_node = self.frame_node.finish()
                self.finished= self.frame_node.parent is None
        return inner_trace

    def __exit__(self, exc_type, exc_value, traceback):
        sys.settrace(self.savetrace)
        if not self.inner:
            root = self.frame_node
            while root.parent is not None:
                root = root.finish()
            root.finish()
            for child in root.children:
                child.report(self.threshold, 0)
            print 'Total elapsed time: %0.3fms' % (root.elapsed * 1000.0)


class notrace(object):

    def __enter__(self):
        self.prev = sys.gettrace()
        sys.settrace(self)

    def __exit__(self, exc_type, exc_value, traceback):
        sys.settrace(self.prev)

    def __call__(self, frame, event, arg):
        return None


def timefunc(threshold=0.1):
    def decorator(f):
        def wrapper(*args, **kw):
            with timetrace(threshold):
                return f(*args, **kw)
        return wrapper
    return decorator


def notimefunc(f):
    def wrapper(*args, **kw):
        with notrace():
            return f(*args, **kw)
    return wrapper


def timeit(name):
    def timeit(f):
        def wrapper(*args, **kw):
            try:
                start = time.time()
                return f(*args, **kw)
            finally:
                print '%s: %0.3fms' % (name, (time.time() - start) * 1000.0)
        return wrapper
    return timeit


class FrameNode(object):

    def __init__(self, frameinfo, parent):
        self.frameinfo = frameinfo
        self.parent = parent
        self.children = []
        self.starttime = time.time()
        if parent:
            parent.children.append(self)
            self.depth = parent.depth + 1
            #print 'ENTER %s%s' % ('  ' * self.depth, frameinfo)
        else:
            self.depth = 0

    def finish(self):
        #print 'EXIT  %s%s' % ('  ' * self.depth, self.frameinfo)
        self.elapsed = time.time() - self.starttime
        return self.parent

    def report(self, threshold, indent):
        elapsed = self.elapsed
        if elapsed >= threshold:
            f = self.frameinfo
            print '%s%s %0.3fms %s %s' % (
                '.' * indent, f.function, elapsed * 1000.0, f.filename, f.lineno)
            for child in self.children:
                child.report(threshold, indent + 1)
