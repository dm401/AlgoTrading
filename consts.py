import logging

# More like config than consts really
THREAD_LIMIT = 6
FORMAT = "%(asctime)s  [%(threadName)s] %(message)s"
LOGLEVEL = logging.INFO
LOGFILE = "logfile.log"
should_clear_logs=True


# Actual consts
base_tingo_url = "https://api.tiingo.com/tiingo/{}"
IG_DEMO_BASE = "https://demo-api.ig.com/gateway/deal/{}"
IG_PROD_BASE = "https://api.ig.com/gateway/deal/{}"

IG_BASE_URL = IG_DEMO_BASE