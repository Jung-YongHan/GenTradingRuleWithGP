
# markets = ('KRW-BTC', 'KRW-ETH')
markets = ('KRW-BTC',)
print(len(markets))

print(len(list(markets)))


ticks = {'a':'value_a', 'b':'value_b'}
for tick in ticks:
    print(tick)

for tick in ticks.keys():
    print(tick)