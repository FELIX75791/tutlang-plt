def factorial(n):
    result = 1
    for _ in range(n):
        result = (result * n)
        n = (n - 1)
    return result
x = 5
print(str("Factorial of 5 is: ") + str(factorial(x)))