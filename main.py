import funcs
import time
import numpy
import logging
import consts
import redis
import requests
# Setup logging to file
logging.basicConfig(format=consts.FORMAT, filename=consts.LOGFILE, level=consts.LOGLEVEL)


class CapitalTracker:
    def __init__(self):
        self.last_update = 0

    def value_to_spend(self):
        if time.time() - self.last_update > 24*60*60:
            self.capital = self.get_capital()
        return self.capital/10

    def get_capital(self):
        # Check if balance is total including amount invested or not
        # This is what we want (total of available + invested.)
        self.capital = requests.get(consts.IG_BASE_URL.format("accounts")).json().get("balance").get("balance")


capital_tracker = CapitalTracker()

def loop(tracked_markets, limit=10, sleeper=2):
    
    value_per_buy = capital_tracker.value_to_spend()
    monitor = 0
    while monitor < 2:
        funcs.get_all_live_data(tracked_markets)

        # curr_rsis = [m.RSI1Day for m in tracked_markets]
        # logging.info("RSIs: ", curr_rsis)

        # curr_adxs = [m.ADX for m in tracked_markets]
        # logging.info("ADXs: ", curr_adxs)
        scores = [m.score for m in tracked_markets]

        buys = []
        rsiPasses = 0
        adxPasses = 0
        macdPasses = 0
        for m in tracked_markets:
            if m.score == 3 :
                buys.append(m.market_name)
            if m.ADX > 25 :
                adxPasses+=1
            if m.RSI1Day < 30 :
                rsiPasses+=1
            if m.MACD > m.MACDYest > m.MACDYestYest and m.MACD > 0:
                macdPasses+=1
        logging.info("BUYS: %s", buys)
        logging.info("macd passes: %s", macdPasses)
        logging.info("adx passes: %s", adxPasses)
        logging.info("rsi passes: %s", rsiPasses)

        logging.info("Scores %s", scores)
        msg = f"Sleeping {sleeper}s, going again! {100*monitor/limit}% {monitor}/{limit}"
        logging.info(msg)
        logging.info("Filtering out invalid markets")
        valid_markets = []
        invalid_markets = []
        for m in tracked_markets:
            if m.score is not None:
                valid_markets.append(m)
            else:
                invalid_markets.append(m.market_name)
        logging.info("Filtered out the following invalid markets %s", invalid_markets)
        tracked_markets = valid_markets
        monitor += 1

        # Here is where we will buy/sell
        for m in tracked_markets:
            m.buysell_if_should(value_per_buy)
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
