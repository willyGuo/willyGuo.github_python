lloyd = {
    "name": "Lloyd",
    "homework": [90.0, 97.0, 75.0, 92.0],
    "quizzes": [88.0, 40.0, 94.0],
    "tests": [75.0, 90.0]
}
alice = {
    "name": "Alice",
    "homework": [100.0, 92.0, 98.0, 100.0],
    "quizzes": [82.0, 83.0, 91.0],
    "tests": [89.0, 97.0]
}
tyler = {
    "name": "Tyler",
    "homework": [0.0, 87.0, 75.0, 22.0],
    "quizzes": [0.0, 75.0, 78.0],
    "tests": [100.0, 100.0]
}

def get_class_average(students):
    results=[]
    for s in students:
        results.append(get_average(s))
    return average(results)
    
def get_letter_grade(score):
    if score>=90:
        return "A"
    if score>=80:
        return "B"
    if score>=70:
        return "C"
    if score>=60:
        return "D"
    return "F"


def average(numbers):
    total=sum(numbers)
    total= float(total)
    return total/len(numbers)
def get_average(student):
    homework = average(student['homework'])
    quizzes = average(student['quizzes'])
    tests = average(student['tests'])
    return homework*0.1+quizzes*0.3+tests*0.6
def	get_student_hw_average(homework):
	
	return sum(homework)/len(homework)
print (get_student_hw_average(alice["homework"]))

#get_letter_grade(get_average(lloyd))
students=[lloyd,alice,tyler]
print (get_letter_grade((get_average(students[1]))))
print (get_class_average(students))
print (get_letter_grade(get_class_average(students)))
