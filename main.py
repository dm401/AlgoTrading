from market_class import Market
from consts import * 
import threading
import time
import numpy
from concurrent.futures import ThreadPoolExecutor, wait

# Read in the markets we want to track from file
with open("markets_to_track.txt", "r") as ffile:
    markets_to_track = ffile.read().splitlines() 

tracked_markets = [Market(market) for market in markets_to_track]
all_threads = [threading.Thread(target=m.getHistorical1Day) for m in tracked_markets]

with ThreadPoolExecutor(max_workers=THREAD_LIMIT) as executor:
    futures_market = [executor.submit(m.getHistorical1Day) for m in tracked_markets]
wait(futures_market)

def get_all_live_data(tracked_markets):
    with ThreadPoolExecutor(max_workers=THREAD_LIMIT) as executor:
        futures_market2 = [executor.submit(m.update) for m in tracked_markets]

    # while not all([f.result() for f in futures_market2]):
    #     print([f.result() for f in futures_market2])
    #     print("Not done")
    #     time.sleep(4)
    # print("Done")
    wait(futures_market2)

last_vals=None
monitor = 1
while monitor < 10:
    get_all_live_data(tracked_markets)
    curr_vals = [m.RSI1Day for m in tracked_markets]
    if last_vals:
        print("Diffs from last poll: ")
        print(numpy.subtract(curr_vals, last_vals))
        
    last_vals = curr_vals

    # for m in markets_to_track:
    #     m.buysell_if_should()

    t_sleep = 2
    print(f"Sleeping {t_sleep}s, going again!")
    monitor += t_sleep
    time.sleep(t_sleep)
