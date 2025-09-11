def add (x , y):
    return x + y

def subtract (x , y):
    return x - y 

def multiply ( x , y):
    return x * y 

def division (x , y):
    return x / y 

print("select operation.")
print("1.add")
print("2.substact")
print("3.multiply")
print("4.divison")

choice = input("enter choice (1/2/3/4):")
num1 = float(input("enter first number:"))
num2 = float(input("enter second number:"))

if choice == "1":
    print(num1, "+", num2, "=", add(num1, num2))

elif choice == "2":   # ✅ correct use of elif
    print(num1, "-", num2, "=", subtract(num1, num2))

elif choice == "3":   # ✅ correct use of elif
    print(num1, "*", num2, "=", multiply(num1, num2))

elif choice == "4":   # ✅ correct use of elif
    print(num1, "/", num2, "=", division(num1, num2))
    if  

else:                 # ✅ falls back if no match
    print("Invalid input")



                                    