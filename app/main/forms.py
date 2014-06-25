from flask.ext.wtf import Form
from wtforms import RadioField, StringField, IntegerField, DateTimeField, 
					SubmitField
from wtforms.validators import Email, Length, Required, NumberRange


class EventForm(Form):
	name = StringField('Event name', validators = [Required()])
	email = StringField('Email address', validators = [Required(), Email()])
	submit = SubmitField('Submit')


class DriverForm(Form):
	name = StringField('Name', validators = [Required()])
	email = StringField('Email address', validators = [Required(), Email()])
	phone = StringField('Phone number', validators = [Required(), Length(10)])
	goingthere = RadioField('Direction', validators = [Required()])
	capacity = IntegerField('Car capacity', validators = [Required(), 
														  NumberRange(1, 10)])
	make_model = StringField('Car make and model', validators = [Required()])
	car_color = StringField('Car color', validators = [Required()])
	datetime = DateTimeField('Departure time', validators = [Required()])
	location = StringField('Location (leaving from/going to)', 
						   validators = [Required()])
	submit = SubmitField('Submit')


class RiderForm(Form):
	name = StringField('Name', validators = [Required()])
	email = StringField('Email address', validators = [Required(), Email()])
	phone = StringField('Phone number', validators = [Required(), Length(10)])
	submit = SubmitField('Submit')

