from flask import render_template, redirect, url_for, abort, flash
from itsdangerous import URLSafeSerializer
from .forms import AddEventForm, AddDriverThereForm, AddDriverBackForm, \
				   EditDriverThereForm, EditDriverBackForm, AddRiderForm
from ..models import Event, Driver, Rider
from . import main
from .. import db


serializer = URLSafeSerializer(current_app.config['SECRET_KEY'])

def generate_token(self):
    return serializer.dumps(self.id)

def find(token):
    try:
        data = serializer.loads(token)
    except:
        return False
    return data


@main.route('/', methods = ['GET', 'POST'])
def index():
	form = AddEventForm()
	if form.validate_on_submit():
		event = Event(name = form.name.data)
		db.session.add(event)
    	db.session.commit()
    	event_token = generate_token(event)
    	return redirect(url_for('show_event', event_token = event_token))
    else:
		return render_template('index.html', form = form)


@main.route('/<event_token>')
def show_event(event_token):
	event = Event.query.get(find(event_token))
	return render_template('event.html', event = event)


@main.route('/<event_token>/<driver_token>', methods = ['GET', 'POST'])
def show_driver(event_token, driver_token):
	event = Event.query.get(find(event_token))
	driver = Driver.query.get(driver(event_token))
	if driver in event.drivers:
		if driver.goingthere:
			form = EditDriverThereForm()
		else:
			form = EditDriverBackForm()
		form.populate_obj(driver)
		if form.validate_on_submit():
			driver.capacity = form.capacity.data
			driver.make_model = form.make_model.data
			driver.car_color = form.car_color.data
			driver.datetime = form.datetime.data
			driver.location = form.location.data
			db.session.commit()
			return redirect(url_for('show_event', event_token = event_token))
		else:
			return render_template('show_driver.html', form = form)
	else:
		return False


@main.route('/<event_token>/add/<driver_type>', methods = ['GET', 'POST'])
def add_driver(event_token, driver_type):
	if driver_type == 'there':
		form = AddDriverThereForm()
		direction_boolean = True
	else if driver_type == 'back':
		form = AddDriverBackForm()
		direction_boolean = False
	else:
		return False
	event = Event.query.get(find(event_token))
	if form.validate_on_submit():
		driver = Driver(goingthere = direction_boolean, 
						name = form.name.data,
						email = form.email.data,
						phone = form.phone.data,
						capacity = form.capacity.data,
						make_model = form.make_model.data,
						car_color = form.car_color.data,
						datetime = form.datetime.data,
						location = form.location.data)
		event.drivers.append(driver)
		db.session.add(driver)
		db.session.commit()
		return redirect(url_for('show_event', event_token = event_token))
	else:
		return render_template('add_driver.html', form = form)


@main.route('/<event_token>/<driver_token>/add', methods = ['GET', 'POST'])
def add_rider(event_token, driver_token):
	event = Event.query.get(find(event_token))
	driver = Driver.query.get(driver(event_token))
	if driver in event.drivers:
		form = AddRiderForm()
		if form.validate_on_submit():
			rider = Rider(name = form.name.data,
						  email = form.email.data,
						  phone = form.phone.data)
			driver.riders.append(rider)
			db.session.add(rider)
			db.session.commit()
			return redirect(url_for('show_event', event_token = event_token))
		else:
			return render_template('add_rider.html', form = form, 
								   driver = driver)
	else:
		return False

