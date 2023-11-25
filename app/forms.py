from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateTimeField
from wtforms.validators import DataRequired, Length


class UnroastedCoffeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    arrival_date = DateTimeField('Arrival Date', validators=[DataRequired()])
    amount = IntegerField('Amount', validators=[DataRequired()])    


class RoastedCoffeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=120)])
    amount = IntegerField('Amount', validators=[DataRequired()])
    roasting_date = DateTimeField('Roasting Date', validators=[DataRequired()])
    order_number = StringField('Order Number', validators=[DataRequired(), Length(max=20)])

