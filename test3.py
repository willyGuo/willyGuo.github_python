n = [3, 5, 7]

def double_list(x):
    for i in range(0, len(x)):
        x[i] = x[i] * 2
    return x

print (n)     #[3,5,7]
for x in n:
	x=x*2
	print (x)   #6\n  10\n   14\n
print (double_list(n)) #[3,5,7]

for	x in n:
	print(x)   #6\n  10\n   14\n
	

n = [3, 5, 7]

def total(numbers):
    result=0
    for n in numbers:
        result+=n
    return (result)
print (total(n))


#print (total2(n))		
