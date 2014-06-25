from flask.ext.wtf import Form
from wtforms import RadioField, StringField, IntegerField, DateTimeField, \
					SubmitField
from wtforms.validators import Email, Length, Required, NumberRange


class AddEventForm(Form):
	name = StringField('Event name', validators = [Required()])
	submit = SubmitField('Submit')


class AddDriverForm(Form):
	name = StringField('Name', validators = [Required()])
	email = StringField('Email address', validators = [Required(), Email()])
	phone = StringField('Phone number', validators = [Required(), Length(10)])
	capacity = IntegerField('Car capacity', validators = [Required(), 
														  NumberRange(1, 10)])
	make_model = StringField('Car make and model', validators = [Required()])
	car_color = StringField('Car color', validators = [Required()])
	datetime = DateTimeField('Departing', validators = [Required()])

class AddDiverThereForm(AddDriverForm):
	location = StringField('Leaving from', validators = [Required()])
	submit = SubmitField('Submit')

class AddDriverBackForm(AddDriverForm):
	location = StringField('Going to', validators = [Required()])
	submit = SubmitField('Submit')


class EditDriverForm(Form):
	capacity = IntegerField('Car capacity', validators = [Required(), 
														  NumberRange(1, 10)])
	make_model = StringField('Car make and model', validators = [Required()])
	car_color = StringField('Car color', validators = [Required()])
	datetime = DateTimeField('Departing', validators = [Required()])

class EditDriverThereForm(EditDriverForm):
	location = StringField('Leaving from', validators = [Required()])
	submit = SubmitField('Submit')

class EditDriverBackForm(EditDriverForm):
	location = StringField('Going to', validators = [Required()])
	submit = SubmitField('Submit')


class AddRiderForm(Form):
	name = StringField('Name', validators = [Required()])
	email = StringField('Email address', validators = [Required(), Email()])
	phone = StringField('Phone number', validators = [Required(), Length(10)])
	submit = SubmitField('Submit')

