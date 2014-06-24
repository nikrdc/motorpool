from flask.ext.wtf import from
from wtforms import RadioField, StringField, IntegerField, DateTimeField, 
					SubmitField
from wtforms.validators import Email, Length, Required, NumberRange


class NewEventForm(Form):
	name = StringField('Event name', validators = [Required()])
	email = StringField('Email address', validators = [Required(), Email()])
	submit = SubmitField('Create')


class NewDriverForm(Form):
	goingthere = RadioField('Direction', validators = [Required()])
	name = StringField('Name', validators = [Required()])
	phone = StringField('Phone number', validators = [Required(), Length(10)])
	email = StringField('Email address', validators = [Required(), Email()])
	capacity = IntegerField('Car capacity', validators = [Required(), 
														  NumberRange(1, 10)])
	make_model = StringField('Car make and model', validators = [Required()])
	car_color = StringField('Car color', validators = [Required()])
	datetime = DateTimeField('Departure time', validators = [Required()])
	location = StringField('Location (leaving from/going to)', 
						   validators = [Required()])
	submit = SubmitField('Create')


class NewRiderForm(Form):
	name = StringField('Name', validators = [Required()])
	phone = StringField('Phone number', validators = [Required(), Length(10)])
	email = StringField('Email address', validators = [Required(), Email()])
	submit = SubmitField('Create')


class EditEventForm(Form):
	