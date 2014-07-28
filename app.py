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


class PersonForm(Form):
    name = StringField('Name')
    phone = StringField('Phone number')
    capacity = IntegerField('Total car capacity (including driver)')
    car_color = StringField('Car color')
    make_model = StringField('Car make and model')
    
    directions = SelectMultipleField(
        'Which direction(s) are you travelling in?',
        choices=[('driving_there', 'I am driving there'), 
                 ('driving_back', 'I am driving back')],
        option_widget=widgets.CheckboxInput(),
        widget = widgets.ListWidget(prefix_label=False))
    
    leaving_from = StringField('Location leaving from')
    leaving_at = DateTimeField('Time departing at')

    going_to = StringField('Location going to')
    going_at = DateTimeField('Time departing at')

    submit = SubmitField('Submit')
    save = SubmitField('Save info')


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
    else:
        return False
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
        flash('Share this page\'s URL with other attendees!')
        return redirect(url_for('show_event', event_token = event_token))
    else:
        return render_template('index.html', form = form)


@app.route('/<event_token>')
def show_event(event_token):
    if find(event_token):
        event = Event.query.get(find(event_token))
        rides_there = [driver for driver in event.drivers.all() if \
                       driver.going_there == True]
        rides_back = [driver for driver in event.drivers.all() if \
                       driver.going_there == False]
        return render_template('event.html', event = event, 
                               event_token = event_token,
                               rides_there = rides_there,
                               rides_back = rides_back)
    else:
        flash('The event you\'re looking for doesn\'t exist!')
        return redirect(url_for('index'))


#AHHAHAHJASHFJHASHSAHAHHAHHA (lol, a comment by alex)

@app.route('/<event_token>/<driver_id>', methods = ['GET', 'POST'])
def show_driver(event_token, driver_id):
    event = Event.query.get(find(event_token))
    driver = Driver.query.get(driver_id)
    if driver in event.drivers:
        form = PersonForm(obj = driver, leaving_from = driver.location,
                          leaving_at = driver.datetime, 
                          going_to = driver.location,
                          going_at = driver.datetime)
        if form.validate_on_submit():
            driver.name = form.name.data
            driver.phone = form.phone.data,
            driver.capacity = form.capacity.data
            driver.car_color = form.car_color.data
            driver.make_model = form.make_model.data
            if driver.going_there:
                driver.location = form.leaving_from.data
                driver.datetime = form.leaving_at.data
            else:
                driver.location = form.going_to.data
                driver.datetime = form.going_at.data
            db.session.add(driver)
            db.session.commit()
            return redirect(url_for('show_event', event_token = event_token))
        else:
            return render_template('driver.html', event_token = event_token,
                                   driver = driver, form = form)
    else:
        abort(404)


@app.route('/<event_token>/<driver_id>/delete', methods = ['POST'])
def delete_driver(event_token, driver_id):
    event = Event.query.get(find(event_token))
    driver = Driver.query.get(driver_id)
    if driver in event.drivers:
        db.session.delete(driver)
        riders = driver.riders
        for rider in driver.riders:
            db.session.delete(rider)
        db.session.commit()
        return redirect(url_for('show_event', event_token = event_token))
    else:
        abort(404)


@app.route('/<event_token>/<driver_id>/<rider_id>/delete', methods = ['POST'])
def delete_rider(event_token, driver_id, rider_id):
    event = Event.query.get(find(event_token))
    driver = Driver.query.get(driver_id)
    rider = Rider.query.get(rider_id)
    if driver in event.drivers and rider in driver.riders:
        db.session.delete(rider)
        db.session.commit()
        return redirect(url_for('show_driver', event_token = event_token,
                                driver_id = driver_id))
    else:
        abort(404)


@app.route('/<event_token>/add', methods = ['GET', 'POST'])
def add_driver(event_token):
    if find(event_token):
        form = PersonForm()
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
        else:
            return render_template('add_driver.html', form = form)
    else:
        abort(404)

#AHHAHAHJASHFJHASHSAHAHHAHHA


@app.route('/<event_token>/<driver_id>/add', methods = ['GET', 'POST'])
def add_rider(event_token, driver_id):
    event = Event.query.get(find(event_token))
    driver = Driver.query.get(driver_id)
    if driver in event.drivers:
        if len(driver.riders.all()) < driver.capacity - 1:
            form = PersonForm()
            if form.validate_on_submit():
                rider = Rider(name = form.name.data,
                              phone = form.phone.data,
                              driver = driver)
                db.session.add(rider)
                db.session.commit()
                return redirect(url_for('show_event', 
                                        event_token = event_token))
            else:
                return render_template('add_rider.html', form = form, 
                                       driver = driver,
                                       event_token = event_token)
        else:
            flash('There isn\'t any space left on that ride!')
            return redirect(url_for('show_event', event_token = event_token))
    else:
        abort(404)




if __name__ == '__main__':
    manager.run()

    