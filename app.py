import os
from flask import Flask, render_template, redirect, session, redirect, \
				  url_for, abort, flash
from flask.ext.script import Manager, Shell
from itsdangerous import URLSafeSerializer
from flask.ext.wtf import Form
from wtforms import StringField, SelectMultipleField, IntegerField, \
                    DateTimeField, SubmitField, widgets
from wtforms.validators import Length, Required, NumberRange
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.moment import Moment


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'substitute key'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

manager = Manager(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, Event=Event, Driver=Driver, Rider=Rider)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


# Models

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))

    drivers = db.relationship('Driver', backref='event', lazy='dynamic')

    def __repr__(self):
        return '<Event %r>' % self.name


class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    going_there = db.Column(db.Boolean) 
    name = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    capacity = db.Column(db.Integer)
    car_color = db.Column(db.String(64))
    make_model = db.Column(db.String(64))
    location = db.Column(db.String(64))
    datetime = db.Column(db.DateTime)

    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    riders = db.relationship('Rider', backref='driver', lazy='dynamic')

    def __repr__(self):
        return '<Driver %r>' % self.name


class Rider(db.Model):
    __tablename__ = 'riders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    phone = db.Column(db.String(64))

    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))

    def __repr__(self):
        return '<Rider %r>' % self.name


# Forms

class EventForm(Form):
    name = StringField('Event name', validators = [Required()])
    submit = SubmitField('Create')


class DriverForm(Form):
    name = StringField('Name', validators = [Required()])
    phone = StringField('Phone number', validators = [Required(), Length(10)])
    capacity = IntegerField('Total car capacity (including driver)', 
                            validators = [Required(), NumberRange(1, 10)])
    car_color = StringField('Car color', validators = [Required()])
    make_model = StringField('Car make and model', validators = [Required()])
    
    directions = SelectMultipleField(
        'Which direction(s) are you travelling in?',
        choices=[('driving_there', 'I am driving there'), 
                 ('driving_back', 'I am driving back')],
        option_widget=widgets.CheckboxInput(),
        widget = widgets.ListWidget(prefix_label=False),
        validators = [Required()])
    
    leaving_from = StringField('Leaving from', validators = [Required()])
    leaving_at = DateTimeField('Leaving at', validators = [Required()])

    going_to = StringField('Going to', validators = [Required()])
    going_at = DateTimeField('Going at', validators = [Required()])

    submit = SubmitField('Submit')


class RiderForm(Form):
    name = StringField('Name', validators = [Required()])
    phone = StringField('Phone number', validators = [Required(), Length(10)])
    submit = SubmitField('Submit')


# Helpers

serializer = URLSafeSerializer(app.config['SECRET_KEY'])

def generate_token(self):
    return serializer.dumps(self.id)

def find(token):
    try:
        data = serializer.loads(token)
    except:
        return False
    return data

def create_driver(form, direction, event):
    if direction == 'driving_there':
        direction_filler = True
        location_filler = 'leaving_from'
        datetime_filler = 'leaving_at'
    elif direction == 'driving_back':
        direction_filler = False
        location_filler = 'going_to'
        datetime_filler = 'going_at'
    driver = Driver(going_there = direction_filler,
                    name = form.name.data,
                    phone = form.phone.data,
                    capacity = form.capacity.data,
                    car_color = form.car_color.data,
                    make_model = form.make_model.data,
                    location = getattr(form, location_filler).data,
                    datetime = getattr(form, datetime_filler).data,
                    event = event)
    return driver


# Errors

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# Routes

@app.route('/', methods = ['GET', 'POST'])
def index():
    form = EventForm()
    if form.validate_on_submit():
        event = Event(name = form.name.data)
        db.session.add(event)
        db.session.commit()
        event_token = generate_token(event)
        return redirect(url_for('show_event', event_token = event_token))
    return render_template('index.html', form = form)


@app.route('/<event_token>')
def show_event(event_token):
    if find(event_token):
        event = Event.query.get(find(event_token))
        return render_template('event.html', event = event)
    flash('The event you\'re looking for doesn\'t exist!')
    return redirect(url_for('index'))


# AIFHIDAFISDF
@app.route('/<event_token>/<driver_token>', methods = ['GET', 'POST'])
def show_driver(event_token, driver_token):
    event = Event.query.get(find(event_token))
    driver = Driver.query.get(find(driver_token))


@app.route('/<event_token>/add', methods = ['GET', 'POST'])
def add_driver(event_token):
    form = DriverForm()
    event = Event.query.get(find(event_token))
    if form.validate_on_submit():
        directions = form.directions.data
        directions_length = len(directions)
        if directions_length == 2:
            driver_there = create_driver(form, directions[0], event)
            driver_back = create_driver(form, directions[1], event)
            db.session.add_all([driver_there, driver_back])
        elif directions_length == 1:
            driver = create_driver(form, directions[0], event)
            db.session.add(driver)
        else:
            return False
        db.session.commit()
        return redirect(url_for('show_event', event_token = event_token))
    return render_template('add_driver.html', form = form)


@app.route('/<event_token>/<driver_token>/add', methods = ['GET', 'POST'])
def add_rider(event_token, driver_token):
    event = Event.query.get(find(event_token))
    driver = Driver.query.get(driver(event_token))
    if driver in event.drivers:
        form = RiderForm()
        if form.validate_on_submit():
            rider = Rider(name = form.name.data,
                          phone = form.phone.data,
                          driver = driver)
            db.session.add(rider)
            db.session.commit()
            return redirect(url_for('show_event', event_token = event_token))
        return render_template('add_rider.html', form = form, driver = driver)
    return False




if __name__ == '__main__':
    manager.run()

    