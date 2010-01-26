import traceback

from karl.log import get_logger

def error_log_middleware(app):
    """
    Logs exceptions to Karl syslog.
    """
    def middleware(environ, start_response):
        try:
            return app(environ, start_response)
        except:
            tb = traceback.format_exc()
            get_logger().error(tb)
            raise

    return middleware

def make_middleware(app, global_config, **config):
    """
    PasteDeploy entry point.
    """
    return error_log_middleware(app)
