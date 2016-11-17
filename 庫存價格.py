shopping_list = ["banana", "orange", "apple"]

stock = {
    "banana": 6,
    "apple": 0,
    "orange": 32,
    "pear": 15
}
    
prices = {
    "banana": 5,
    "apple": 2,
    "orange": 1.5,
    "pear": 5
}

# Write your code below!
def compute_bill(food):
    total =0
    for i in food:
        if stock[i]>0:
            total =total+prices[i]
            stock[i]=stock[i]-1
    return total
    
for i in 10:
	print('1')