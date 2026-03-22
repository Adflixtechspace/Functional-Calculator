from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired

class CalculatorForm(FlaskForm):
    expression = StringField("Input math expression here:", validators=[InputRequired()])
    result = StringField("Result:")
    submit = SubmitField("Calculate")

class FunctionMakerForm(FlaskForm):
    name = StringField("Input name of function here:", validators=[InputRequired()])
    expr = StringField("Input expression of function here:", validators=[InputRequired()])
    submit = SubmitField("Create Function")