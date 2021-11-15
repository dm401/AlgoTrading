from Market import Market

markets_to_track = ["pfe", "ibm"]

tracked_markets = [Market(market) for market in markets_to_track]

for m in tracked_markets:
    print(m.market)
    m.update()
    print(m.RSI1Day)
