"""from random	import randint
willy={'a':[100,200,300]}
print (willy)

def add_dic_end(valuesend):
	list=[]
	list=valuesend['a']
	for i in range(90,95):
		x=randint(0,5)
		print(x,i)
		list.append(i+x)
		valuesend['a']=list
	
	return valuesend
print (add_dic_end(willy))

guess_row = input("Guess Row:")
guess_col = input("Guess Col:")

print(guess_row,guess_col)
print(type(guess_col))
print(type(guess_row))
sum=int(guess_col)+5
print(sum)"""
"""#正常的KEYS加值	
list=[]
list = willy['a']
list.append(400)
willy['a']=list
print(willy)

#比較厲害的一行KEYS加值
dic['a'] = dic['a'].append(500)

def digit_sum(x):
	sum=0
	for i in x:
		sum+=i
	return sum

a=[10,20,30]
print (digit_sum(a))

for n in range(5):
	print(n)
m='mygod'
x=[]
x=m[1]
print(x)

score = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2, 
         "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3, 
         "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1, 
         "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4, 
         "x": 8, "z": 10}
         
def scrabble_score(word):
    n=0
    for i in word.lower():
        n+=score[i]
    return n
print (scrabble_score('score'))
print (score['a'])
a = "Free your mind."
b = "Welcome to the desert... of the real."
c = "What is real? How do you define real?"
d = "There is no spoon."
 
print(a)
print(a.split())
print()
 
print(b)
print(b.split("o"))
print()
 
print(c)
print(c.split(" ", 2))
print()
 
print(d)
print(d.split("a"))
print()

llist=[5,'dwdw','fewef']
print("".join([str(r) for r in llist]))

def list_to_str(llist):
	y=[]
	for r in llist:
		x=str(r)
		y.append(x)
	print('**'.join(y))
		
a=[12312,'dqdqwd',4124,'ff']
list_to_str(a)

list_a=['a','b','c','d']
list_reverse=list_a[::-1]
print(list_reverse)	

list_str="abcdefg"
list_str_reverse=list_str[::-1]
print(list_str_reverse)

def median(x):
    sorted_x=sorted(x)
    if len(x)%2!=0:
        return sorted_x[len(x)//2]
    else:
        return (sorted_x[len(x)//2]+sorted_x[len(x)//2-1])/2.0
		
dd=[1,2,3,4,5,6,7,8]
print (median(dd))

grades = [100, 100, 90, 40, 80, 100, 85, 70, 90, 65, 90, 85, 50.5]

def print_grades(grades):
	g_list=[]
	for g in grades:
		g_list.append(g)
	print(g_list)
        
print_grades(grades)
print(grades)

for i in range(10):
    print(i)


dic={"a":45,"b":'cool',"c":{"a1":45,"b2":'cool',"c3":'good'}}
print(dic["c"]["a1"])
c=dic["c"]["a1"]"""



"""
 
def censor(text):
	n=[]
	split_text=text.split()
	for i in split_text:
		print (i)
		for a in i:
			if a != 'X':
				n.append(a)
			else:
				False
	n=" ".join(n)
	n=n[::-1]
	print(n)
	
censor(garbled)

garbled = "!XeXgXaXsXsXeXmX XtXeXrXcXeXsX XeXhXtX XmXaX XI"
def censor(text):
	new_text=[]
	for i in text:
		if i !='X':
			new_text.append(i)
	print("".join(new_text[::-1]))
censor(garbled)    
print(type(filter(lambda c: c!='X',garbled)))
message=list(filter(lambda c: c!='X',garbled))
print("".join(message)[::-1])


def fun1():
	for i in range(1,10,3):
		for j in range(1,10):
			print("%d * %d=%d	%d * %d=%d\t	%d * %d=%d" %(i,j,i*j,(i+1),j,(i+1)*j,(i+2),j,(i+2)*j))

		print("-----------------------------------------")

print(fun1())
print ('\n'.join(['\t'.join(['%d*%d=%d' % (j,i,i*j) for i in range(1,10)]) for j in range(1,10)]) )
print("-----------------------------------next work---------------------")"""
for i in range(1, 10):
        for j in range(1, 10):
            print('{}x{}={}\t'.format(i, j, i*j), end='')
        print()
print("-----------差別--------")
for i in range(1,10,3):
	for j in range(1,10):
		print('{}x{}={}\t {}x{}={}\t {}x{}={}\t'.format(i,j,i*j,(i+1),j,(i+1)*j,(i+2),j,(i+2)*j ) )
	print()	
	
print("-----------差別2--------")
for i in range(1,10,3):
	for j in range(1,10):
		print('%d*%d=%d\t %d*%d=%d\t %d*%d=%d\t'%(i,j,i*j,(i+1),j,(i+1)*j,(i+2),j,(i+2)*j ) )
	print()	
	