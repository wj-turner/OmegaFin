import tpqoa

oanda = tpqoa.tpqoa('./oanda.cfg')

ins = oanda.get_instruments()

print(ins)