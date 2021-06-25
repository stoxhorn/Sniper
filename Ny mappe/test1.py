import defi.defi_tools as dft

metadata, df = dft.getProtocol('Pancakeswap')

pairs = dft.pcsPairInfo("BNB", "CAKE")
print(pairs)

