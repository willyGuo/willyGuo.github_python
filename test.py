#coding:utf-8

print ("helo world")
a="得名"
print (a*10)

for r in range(5,10):
	print(r)
print(len(a))
if len(a*10)>10:
   print("很長")
else:
	print("很短")
 
def shut_down(s):
    if s=="yes":
        return "Shut_down"
    elif s=="no":
        return "Shutdown aborted"
    return "Sorry"



my_list=[1,8,5,4]
for n in my_list:
	print (n)
sum=0
for n in my_list:
	sum+=n
	print (sum)
	
inventory = {
    'pocket'   : ['seashell', 'strange berry', 'lint'],
    'gold'     : 500,
    'pouch'    : ['flint', 'twine', 'gemstone'], 
    'backpack' : ['xylophone','dagger', 'bedroll','bread loaf']
}

# Adding a key 'burlap bag' and assigning a list to it
inventory['burlap bag'] = ['apple', 'small ruby', 'three-toed sloth']
print(inventory)
print("--------------------------------\n")
inventory['backpack'].sort()
inventory['backpack'].remove('dagger')
inventory['gold']+=50

print(inventory)




shopping_list = ["banana", "orange", "apple"]

stock = {
    "banana": 8,
    "apple": 0,
    "orange": 32,
    "pear": 15
}
    
prices = {
    "banana": 4,
    "apple": 2,
    "orange": 1.5,
    "pear": 3
}

# Write your code below!
def compute_bill(food):
    total =0
    for i in food:
        total =total+prices[i]
    return total
for i in range(10)
	print("update")
	
print("branch")

    