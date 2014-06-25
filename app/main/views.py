from flask import render_template, redirect, url_for, abort, flash
from .forms import EventForm, DriverForm, RiderForm
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
	form = EventForm()
	if form.validate_on_submit():
		event = Event(name = form.name.data)
		db.session.add(event)
    	db.session.commit()
    	event_token = generate_token(event)
    	return redirect(url_for('show_event', event_token = event_token))
	return render_template('index.html', form = form)


@main.route('/<event_token>')
def show_event(event_token):
	event_id = find(event_token)


@main.route('/<event_token>/<driver_token>', methods = ['GET', 'POST'])
def show_driver(event_token, driver_token):
	event_id = find(event_token)
	driver_id = find(driver_token)


@main.route('/<event_token>/add/<driver_type>', methods = ['GET', 'POST'])
def add_driver(event_token, driver_type):
	event_id = find(event_token)


@main.route('<event_token>/<driver_token>/add', methods = ['GET', 'POST'])
def add_rider(event_token, driver_token):
	event_id = find(event_token)
	driver_id = find(driver_token)

