import logging

# More like config than consts really
THREAD_LIMIT = 6
FORMAT = "%(asctime)s  [%(threadName)s] %(message)s"
LOGLEVEL = logging.INFO
LOGFILE = "logfile.log"
should_clear_logs=True