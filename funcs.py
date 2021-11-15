from market_class import Market
from consts import * 
import threading
from concurrent.futures import ThreadPoolExecutor, wait


def get_markets():
    """
    Returns an iterable of the markets we track
    """
    # Read in the markets we want to track from file
    with open("markets_to_track.txt", "r") as ffile:
        markets_to_track = ffile.read().splitlines() 

    tracked_markets = [Market(market) for market in markets_to_track]
    return tracked_markets

def get_historical_data(tracked_markets):
    """
    Submits the get historical func to a thread pool to populate the 
    data for each tracked market
    """
    all_threads = [threading.Thread(target=m.getHistorical1Day) for m in tracked_markets]

    with ThreadPoolExecutor(max_workers=THREAD_LIMIT) as executor:
        historical_futures = [executor.submit(m.getHistorical1Day) for m in tracked_markets]
    wait(historical_futures)

def get_all_live_data(tracked_markets):
    """
    Gets the live data for all markets
    """
    with ThreadPoolExecutor(max_workers=THREAD_LIMIT) as executor:
        futures_market = [executor.submit(m.update) for m in tracked_markets]
    wait(futures_market)

