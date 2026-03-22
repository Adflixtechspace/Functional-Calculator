from flask import Flask, render_template
from database import get_db, close_db
from forms import CalculatorForm, FunctionMakerForm
import math

app = Flask(__name__)
app.config["SECRET_KEY"] = "egg"
app.teardown_appcontext(close_db)

# Helper function to convert expression to callable function
def convert_to_function(expr):
    """Convert a string expression into a callable function"""
    def user_function(x=1, y=1, z=1):
        return eval(expr, {"x": x, "y": y, "z": z, "math": math})
    return user_function

# Helper function to load functions from database
def load_functions():
    """Load all functions from database into a dictionary"""
    db = get_db()
    list_of_functions = db.execute("SELECT name, expression FROM functions ORDER BY name;").fetchall()
    functions = {}
    for name, expr in list_of_functions:
        functions[name] = convert_to_function(expr)
    return functions

# Initialise database on startup
with app.app_context():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS functions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            expression TEXT NOT NULL
        );
    """)
    db.commit()

@app.route("/")
def home():
    return render_template("index.html", title="Functional Calculator - Home")

@app.route("/calculator", methods=['GET', 'POST'])
def calculator():
    
    form = CalculatorForm()
    functions = load_functions()
    db = get_db()
    functions_list = db.execute("SELECT name, expression FROM functions ORDER BY name;").fetchall()
    error=''
    
    if form.validate_on_submit():
        try:
            expression = form.expression.data.replace('^', '**')
            form.result.data = eval(expression, {"__builtins__": None}, {"math": math, **functions})
        except NameError:
            error = "Unknown function or variable. Did you define it?"
            form.result.data = "Error"
        except SyntaxError:
            error = "Error. Check your parentheses or operators."
            form.result.data = "Error"
        except ZeroDivisionError:
            error = "Cannot divide by zero."
            form.result.data = "Error"
        except TypeError:
            error = "Invalid operation. Maybe you forgot parentheses?"
            form.result.data = "Error"
        except Exception as e:
            error = f"Unexpected error: {e}"
            form.result.data = "Error"
        
    return render_template("calculator.html", title="Functional Calculator - Calculator mode", form=form, functions=functions, functions_list=functions_list, error=error)

@app.route("/function_maker", methods=['GET', 'POST'])
def functionMaker():
    form = FunctionMakerForm()
    functions = load_functions()
    db = get_db()
    functions_list = db.execute("SELECT name, expression FROM functions ORDER BY name;").fetchall()
    error = ''
    success = None
    
    if form.validate_on_submit():
        name = form.name.data
        expr = form.expr.data
        expr = expr.replace('^', '**')
        
        try:
            # Validate the expression before saving
            test_func = convert_to_function(expr)
            test_func()  # Test with default values
            
            if " " not in name:
                # Save to database
                db.execute("INSERT OR REPLACE INTO functions (name, expression) VALUES (?,?);", (name, expr))
                db.commit()
            
                success = f"Function '{name}' saved successfully!"
            else:
                error = "Invalid expression syntax. No spaces allowed in the function name."
            
            # Clear form and reload functions
            form.name.data = ""
            form.expr.data = ""
            functions = load_functions()
            functions_list = db.execute("SELECT name, expression FROM functions ORDER BY name;").fetchall()
            
        except SyntaxError:
            error = "Invalid expression syntax. Check your expression."
        except NameError as e:
            error = f"Invalid variable or function in expression."
        except Exception as e:
            error = f"Error creating function: {e}"
        
    return render_template("functionMaker.html", title="Functional Calculator - Function Maker mode ", 
                         form=form, functions=functions, functions_list=functions_list, error=error, success=success)