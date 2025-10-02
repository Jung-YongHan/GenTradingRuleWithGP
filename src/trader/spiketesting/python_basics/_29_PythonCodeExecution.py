


function = """
def buy(price, abc):
    print(price, abc)
    return True
    
def sell(price, abc):
    print(price, abc['test'])
    return True
"""

exec(function)
global buy, sell

print(buy(123, 322))

print(sell(123,{'test':'xxx'}))

#################################################

def buy(price, abc):
    print(price, abc)
    return True

def sell(price, abc):
    print(price, abc['test'])
    return True

print(buy(123, 322))
print(sell(123,{'test':'xxx'}))