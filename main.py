from market_class import Market
import threading
import time
import numpy

with open("markets_to_track.txt", "r") as ffile:
    markets_to_track = ffile.read().splitlines() 

tracked_markets = [Market(market) for market in markets_to_track]
all_threads = [threading.Thread(target=m.getHistorical1Day) for m in tracked_markets]

# Start all the http reqs
for t in all_threads:
    print("Starting thread", t)
    t.start()

# Wait for all threads to finish before continuing
for t in all_threads:
    print("Joining", t)
    t.join()


def get_all_live_data(tracked_markets):
    all_t = [threading.Thread(target=m.update) for m in tracked_markets]
    for t in all_t:
        t.start()
    
    for t in all_t:
        t.join()

    for m in tracked_markets:
        print()
        print(m.market)
        print(m.RSI1Day)

last_vals=None
monitor = 1
while monitor < 10:
    get_all_live_data(tracked_markets)
    curr_vals = [m.RSI1Day for m in tracked_markets]
    if last_vals:
        print("Diffs from last poll: ")
        print(numpy.subtract(curr_vals, last_vals))
        
    last_vals = curr_vals

    print("Slept 1s, going again!")
    monitor += 2
    time.sleep(2)
