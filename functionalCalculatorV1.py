# This is the original Functional Calculator I made in 2025 before I learnt how to use Flask. I wanted to learn how to make a GUI for my application so I waited until I learnt it in college to return and implement my knowledge now.

# This program is called "Functional Calculator" and it is a usable calculator that allows to create functions and then use those functions combined to solve mathematical problems. This program will have multiple purposes.

# 1. A set of functions that will allow the program to talk to a functions database via SQLite are initialised for future use.

# 2. This program will prompt the user on a variety of possible actions. They can use a calculator mode, or they can create new functions that can be used for as long as the program is active for.

# 3. If the user chooses to create a new function, they will be prompted to name their function. After this, they will be asked to create a function in relation to a variable x, y and z (undefined values default to 1). The program will convert this into a mathematical function and save it for future use.

# 4. If the user chooses to use the calculator, it will function like a standard calculator, allowing to add, subtract, etc. The key difference with this calculator is that the functions created can be passed into the calculator.

# Note: The program will allow the user to switch between function creator and calculator on the fly using the keyword 'switch', and quit the program using the keyword 'quit'.

# math module is useful for using built-in functions, increasing accuracy and saving time inputting into the database, as long as user uses 'math' keyword in calculator, sqlite3 allows functions to be saved in a database for future use after the program quits.

import math
import sqlite3

def main():
    initdb()
    functions = {}

    for name, expr in readfromdb():
        functions[name] = convertToFunction(expr)
    
    current_mode = initiationPage()
    while current_mode != 'quit':
        if current_mode == '1':
            current_mode = calculatorMode(functions)
        elif current_mode == '2':
            current_mode = functionMaker(functions)

# 1. These set of functions handle interactions with the SQLite database used to store the functions used in this program.

# 1a: This function initialises a functions database if such database does not exist yer.

def initdb():
    connection = sqlite3.connect("functions.sqlite")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS functions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            expression TEXT NOT NULL
        );
    """)
    connection.commit()
    connection.close()

# 1b: This function inserts the newly created function into the database for use in function maker mode.

def addtodb(name, expr):
    connection = sqlite3.connect("functions.sqlite")
    cur = connection.cursor()
    cur.execute("INSERT OR REPLACE INTO functions (name, expression) VALUES (?,?);", (name, expr))
    connection.commit()
    connection.close()

# 1c: This function reads the name and expression columns of the database for use in calculator mode.

def readfromdb():
    connection = sqlite3.connect("functions.sqlite")
    cur = connection.cursor()
    cur.execute("SELECT name, expression FROM functions;")
    rows = cur.fetchall()
    connection.close()
    return rows

# 1d: This function deletes specific rows of a database for functions you may want to remove entirely.

def deletefromdb(name):
    connection = sqlite3.connect("functions.sqlite")
    cur = connection.cursor()
    cur.execute("DELETE FROM functions WHERE name = ?;", (name,))
    connection.commit()
    connection.close()

# 2. This function will ask the user for a mode of choice and with this, return the choice made by the user.

def initiationPage():
    choice = input("Please select the mode you want to enter. 1 for calculator mode, 2 for function creator mode: ")

    if choice == '1' or choice == '2':
        return choice
    else:
        return initiationPage()

# 3a. This section is split into a few parts. 'convertToFunction' takes the inputs from functionMaker and returns an actual function that can be used in the calculator mode. It can create function up to 3 variables x, y and z.

def convertToFunction(expr):
    def userFunction(x=1, y=1, z=1):
        return eval(expr, {"x": x, "y": y, "z": z, "math": math})
    return userFunction

# 3b. This function can be used in either mode and displays all your current functions to the console.

def list_functions(functions):
    if not functions:
        print("No functions defined yet.")
    else:
        print("Available functions:")
        for name in functions:
            print("-", name)


# 3c. 'functionMaker' meanwhile is responsible for taking inputs in from the user in order to hand over to convertToFunction to create the function to be used in the calculator mode.

def functionMaker(functions):
    functionName = ''
    print("In Function Maker Mode, you can specify a valid function name and you will then be prompted to input the expression. \nThere are also a variety of commands you can use, including: \nswitch - switches program to calculator mode, \nfunctions - allows you to view all currently created functions, \ndelete - prompts you to delete a function from the database, and \nquit - quits the program.")
    while functionName != 'switch' and functionName != 'quit':
        functionName = input("Give function name: ")

        if functionName == 'switch':
            print('switching to Calculator...')
            return '1'
        
        elif functionName == 'functions':
            list_functions(functions)
            continue

        elif functionName == 'delete':
            name = input("Which function do you want to delete: ")
            if name in functions:
                deletefromdb(name)
                functions.pop(name)
                print(f"Function '{name}' deleted.") 
            else:
                print(f"No function named '{name}' found.")
            continue
              

        elif not functionName.isidentifier():
            print("Invalid function name. Names must start with a letter or underscore, and contain only letters, numbers, or underscores.")
            continue
        
        elif functionName == 'quit':
            exit()

        else:
            functionItself = input("Give the function in terms of x, y, z (unused variables default to 1): ")
            functions[functionName] = convertToFunction(functionItself)
            addtodb(functionName, functionItself)

# 4. This function asks the user for an input to evaluate the mathematical expression. This can be numbers or functions. Once done, it returns the result.

def calculatorMode(functions):
    mathExpression = ''
    print("In Calculator Mode, you can input mathematical expressions using numbers, operators, and functions you create and it will return the output. \nThere are also a variety of commands you can use, including: \nswitch - switches program to calculator mode, \nfunctions - allows you to view all currently created functions, and \nquit - quits the program.")
    while mathExpression != 'switch' and mathExpression != 'quit':
        mathExpression = input("Input math expression here: ")

        if mathExpression == 'switch':
            print('switching to Function Maker...')
            return '2'
        
        elif mathExpression == 'functions':
            list_functions(functions)
            continue

        elif mathExpression == 'quit':
            exit()

        try:
            print(eval(mathExpression, {"__builtins__": None}, {"math": math, **functions}))
        except NameError:
            print("Unknown function or variable. Did you define it?")
        except SyntaxError:
            print("Syntax error. Check parentheses or operators.")
        except TypeError:
            print("Invalid operation. Maybe you forgot parentheses or used a function wrong?")
        except Exception as e:
            print("Unexpected error:", e)

main()