from Market import Market

ibm = Market("pfe")
ibm.getHistorical1Day()
ibm.getLivePrice()
ibm.getRSI1Day()

print (ibm.data)
print(ibm.RSI1Day)