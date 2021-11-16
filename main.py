import funcs
import time
import numpy

def loop(tracked_markets, limit=10, sleeper=2):
    last_vals=None
    monitor = 0
    while monitor < 10:
        funcs.get_all_live_data(tracked_markets)
        curr_vals = [m.RSI1Day for m in tracked_markets]
        # if last_vals:
        #     print("Diffs from last poll: ")
        #     print(numpy.subtract(curr_vals, last_vals))
        #
        # last_vals = curr_vals

        # for m in markets_to_track:
        #     m.buysell_if_should()

        print(curr_vals)

        print(f"Sleeping {sleeper}s, going again! {100*monitor/limit}% {monitor}/{limit}")
        monitor += sleeper
        time.sleep(sleeper)


if __name__=="__main__":
    markets = funcs.get_markets()
    funcs.get_historical_data(markets)
    loop(markets)
