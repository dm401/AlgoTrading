import funcs
import time
import numpy
import logging
import consts

# Setup logging to file
logging.basicConfig(format=consts.FORMAT, filename=consts.LOGFILE, level=consts.LOGLEVEL)


def loop(tracked_markets, limit=10, sleeper=2):

    monitor = 0
    while monitor < 2:
        funcs.get_all_live_data(tracked_markets)

        # curr_rsis = [m.RSI1Day for m in tracked_markets]
        # logging.info("RSIs: ", curr_rsis)

        # curr_adxs = [m.ADX for m in tracked_markets]
        # logging.info("ADXs: ", curr_adxs)
        scores = [m.score for m in tracked_markets]
        logging.info("Scores %s", scores)
        msg = f"Sleeping {sleeper}s, going again! {100*monitor/limit}% {monitor}/{limit}"
        logging.info(msg)
        logging.info("Filtering out invalid markets")
        valid_markets = []
        for m in tracked_markets:
            if not m.score:
                logging.info("Dropped %s as it got an invalid API resp", m.market_name)
            else:
                valid_markets.append(m)
        logging.info("Filtered out invalid markets")
        tracked_markets = valid_markets
        monitor += 1
        time.sleep(sleeper)


if __name__ == "__main__":
    if consts.should_clear_logs:
        with open('logfile.log', 'r+') as ffile:
            ffile.truncate(0)
    logging.info("Starting...")
    markets = funcs.get_markets("markets_to_track.txt")
    logging.info("Getting historical data")
    funcs.get_historical_data(markets)
    logging.info("Got historical data, now looping for live data")
    loop(markets)
