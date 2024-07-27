import sys
from traceback import format_exception
import excepthook
from debug_utils import _addTagsToMsg, _makeMsgHeader, LOG_CURRENT_EXCEPTION, _src_file_trim_to, _g_logLock
from threading import Lock

from .ILogger import ILogger

loggerLock = Lock()

def _currentExceptionToString(tags=None, frame=1):
  msg = _makeMsgHeader(sys._getframe(frame)) + '\n'
  etype, value, tb = sys.exc_info()
  msg += ''.join(format_exception(etype, value, tb, None))
  with _g_logLock:
    line = '[EXCEPTION]' + _addTagsToMsg(tags, msg)
    extMsg = excepthook.extendedTracebackAsString(_src_file_trim_to, None, None, etype, value, tb)
    if extMsg:
      line += '[EXCEPTION]' + _addTagsToMsg(tags, extMsg)
  return line

def withExceptionHandling(logger=None):
  # type: (ILogger) -> Callable
  def inner_decorator(f):
    def wrapped(*args, **kwargs):
      try:
        return f(*args, **kwargs)
      except:
        if logger:
          with loggerLock:
            logger.critical(_currentExceptionToString())
        else:  
          LOG_CURRENT_EXCEPTION()
    return wrapped
  return inner_decorator

def logCurrentException(prefix=None, logger=None, level='CRITICAL'):
  # type: (str, ILogger, str) -> None
  if logger:
    msg = prefix + '\n' if prefix else ''
    msg += _currentExceptionToString()
    logger.printLog(level, msg)
  else:
    LOG_CURRENT_EXCEPTION()
