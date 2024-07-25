import sys
from traceback import format_exception
import excepthook
from debug_utils import _addTagsToMsg, _makeMsgHeader, LOG_CURRENT_EXCEPTION, _src_file_trim_to, _g_logLock
from Event import Event

from .Logger import Logger

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

def withExceptionHandling(logger=Logger.instance()):
  def inner_decorator(f):
    def wrapped(*args, **kwargs):
      try:
        return f(*args, **kwargs)
      except:
        if logger:
          logger.critical(_currentExceptionToString())
        else:  
          LOG_CURRENT_EXCEPTION()
    return wrapped
  return inner_decorator

def logCurrentException(prefix=None, logger=Logger.instance(), level='CRITICAL'):
  if logger:
    msg = prefix + '\n' if prefix else ''
    msg += _currentExceptionToString()
    logger.printLog(level, msg)
  else:
    LOG_CURRENT_EXCEPTION()

class SendExceptionEvent(Event):
  def __init__(self, logger=Logger.instance()):
    super(SendExceptionEvent, self).__init__(None)
    self.logger = logger

  def __call__(self, *args, **kwargs):
    for delegate in self[:]:
      try:
        delegate(*args, **kwargs)
      except:
        if self.logger:
          self.logger.critical(_currentExceptionToString())
        else:
          LOG_CURRENT_EXCEPTION()