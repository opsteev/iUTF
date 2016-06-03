import logging
from logging.handlers import MemoryHandler
import sys
import types

__all__ = ['Ilogger', 'FileAdapter']

def customEmit(self, record):
    # Monkey patch Emit function to avoid new lines between records
    try:
        #print("Current hknewline %r\n"% hknewline.newline)
        if self.need_format:
            msg = self.format(record)
            if hknewline.newline:
                msg = '\n%s'%msg
                hknewline.newline = False
        else:
            msg = record.getMessage()
            hknewline.newline = False
        if not hasattr(types, "UnicodeType"): #if no unicode support...
            self.stream.write(msg)
        else:
            try:
                if getattr(self.stream, 'encoding', None) is not None:
                    self.stream.write(msg.encode(self.stream.encoding))
                else:
                    self.stream.write(msg)
            except UnicodeError:
                self.stream.write(msg.encode("UTF-8"))
        self.flush()
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        self.handleError(record)

class HackNewlineInTheBegin(object):
    '''
    To format the log, make this hack
    '''
    def __init__(self):
        self.newline = False

hknewline = HackNewlineInTheBegin()

class CustomizedStreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        logging.StreamHandler.__init__(self, stream)
        self.need_format = True
    def emit(self, record):
        customEmit(self, record)

class CustomizedMemoryHandler(MemoryHandler):
    def __init__(self, capacity, flushLevel=logging.ERROR, target=None):
        MemoryHandler.__init__(self, capacity, flushLevel=flushLevel, target=target)
    def shouldFlush(self, record):
        msg = record.getMessage()
        if msg and (msg[-1] in '\r\n'):
            return True
        return False

class Ilogger(object):
    def __init__(self, name, logfile=None, loglevel=logging.INFO):

        self.DEVICE = 100

        self.logger = logging.getLogger(name)

        self.name = name
        self.logfile = logfile
        self.loglevel = loglevel

        self.logger.setLevel(self.loglevel)
        self.formatter = logging.Formatter('%(asctime)s | %(levelname)8s | %(name)16s : %(message)s')

        self.chandler = CustomizedStreamHandler()
        #self.mhandler = CustomizedMemoryHandler(100000, target=self.chandler)
        self.chandler.setFormatter(self.formatter)
        self.logger.addHandler(self.chandler)

        if self.logfile:
            self.fhandler = logging.FileHandler(self.logfile)
            self.fhandler.setFormatter(self.formatter)
            self.logger.addHandler(self.fhandler)

        logging.addLevelName(self.DEVICE, 'DEVICE')

    def set_level(self, loglevel):
        self.logger.setLevel(loglevel)

    def debug(self, msg, *args, **kwargs):
        self.chandler.need_format = True
        msg = '%r\n'%str(msg)
        self.logger.debug(msg, *args, **kwargs)
        #hknewline.newline = False

    def info(self, msg, *args, **kwargs):
        self.chandler.need_format = True
        msg = '%r\n'%str(msg)
        self.logger.info(msg, *args, **kwargs)
        #hknewline.newline = False

    def warning(self, msg, *args, **kwargs):
        self.chandler.need_format = True
        msg = '%r\n'%str(msg)
        self.logger.warning(msg, *args, **kwargs)
        #hknewline.newline = False

    def error(self, msg, *args, **kwargs):
        self.chandler.need_format = True
        msg = '%r\n'%str(msg)
        self.logger.error(msg, *args, **kwargs)
        #hknewline.newline = False

    def exception(self, msg, *args, **kwargs):
        self.chandler.need_format = True
        msg = '%r\n'%str(msg)
        kwargs["exc_info"] = 1
        self.logger.error(msg, *args, **kwargs)
        #hknewline.newline = False

    def critical(self, msg, *args, **kwargs):
        self.chandler.need_format = True
        msg = '%r\n'%str(msg)
        kwargs["exc_info"] = 1
        self.logger.critical(msg, *args, **kwargs)
        #hknewline.newline = False

    def log(self, level, msg, *args, **kwargs):
        self.logger.log(level, msg, *args, **kwargs)

    def device(self, msg, *args, **kwargs):
        #self.logger.log(self.DEVICE, msg, *args, **kwargs)
        if msg:
            lines = msg.splitlines()
            endline = lines.pop()
            for line in lines:
                self.logger.log(self.DEVICE, '%s\n', line, *args, **kwargs)
                self.chandler.need_format = True
            if msg[-1] in '\r\n':
                self.logger.log(self.DEVICE, '%s\n', endline, *args, **kwargs)
                self.chandler.need_format = True
            else:
                self.logger.log(self.DEVICE, endline, *args, **kwargs)
                self.chandler.need_format = False
                #print("Change hknewline to True\n")
                hknewline.newline = True

if '-vv' in sys.argv or '-vvv' in sys.argv:
    log = Ilogger('IUTF', loglevel = logging.DEBUG)
else:
    log = Ilogger('IUTF', loglevel = logging.INFO)

class FileAdapter(object):
    def __init__(self, logger):
        self.logger = logger
    def write(self, data):
        if data.strip('\r\n'):
            self.logger.device(data)
    def flush(self):
        pass  # leave it to logging to flush properly