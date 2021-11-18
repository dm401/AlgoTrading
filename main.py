import funcs
import time
import numpy

def loop(tracked_markets, limit=10, sleeper=2):

    monitor = 0
    while monitor < 10:
        funcs.get_all_live_data(tracked_markets)

        curr_rsis = [m.RSI1Day for m in tracked_markets]
        print("RSIs: ", curr_rsis)

        #curr_adxs = [m.ADX for m in tracked_markets]
        #print("ADXs: ", curr_adxs)

        print(f"Sleeping {sleeper}s, going again! {100*monitor/limit}% {monitor}/{limit}")
        monitor += sleeper
        time.sleep(sleeper)


if __name__=="__main__":
    markets = funcs.get_markets()
    funcs.get_historical_data(markets)
    loop(markets)
