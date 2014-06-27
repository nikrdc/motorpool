import os
from flask import Flask, render_template, redirect, session, redirect, \
				  url_for, abort, flash
from flask.ext.script import Manager, Shell
from itsdangerous import URLSafeSerializer
from flask.ext.wtf import Form
from wtforms import StringField, IntegerField, DateTimeField, SubmitField
from wtforms.validators import Length, Required, NumberRange
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.moment import Moment

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
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
    goingthere = db.Column(db.Boolean) 
    name = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    capacity = db.Column(db.Integer)
    make_model = db.Column(db.String(64))
    car_color = db.Column(db.String(64))
    datetime = db.Column(db.DateTime)
    location = db.Column(db.String(64))

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

class AddEventForm(Form):
    name = StringField('Event name', validators = [Required()])
    submit = SubmitField('Create')


class AddDriverForm(Form):
    name = StringField('Name', validators = [Required()])
    phone = StringField('Phone number', validators = [Required(), Length(10)])
    capacity = IntegerField('Car capacity', validators = [Required(), 
                                                          NumberRange(1, 10)])
    make_model = StringField('Car make and model', validators = [Required()])
    car_color = StringField('Car color', validators = [Required()])
    datetime = DateTimeField('Departing', validators = [Required()])

class AddDriverThereForm(AddDriverForm):
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
    phone = StringField('Phone number', validators = [Required(), Length(10)])
    submit = SubmitField('Submit')


# 

serializer = URLSafeSerializer(app.config['SECRET_KEY'])

def generate_token(self):
    return serializer.dumps(self.id)

def find(token):
    try:
        data = serializer.loads(token)
    except:
        return False
    return data


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# Routes

@app.route('/', methods = ['GET', 'POST'])
def index():
    form = AddEventForm()
    if form.validate_on_submit():
        event = Event(name = form.name.data)
        db.session.add(event)
        db.session.commit()
        event_token = generate_token(event)
        return redirect(url_for('show_event', event_token = event_token))
    return render_template('index.html', form = form)


@app.route('/<event_token>')
def show_event(event_token):
    event = Event.query.get(find(event_token))
    return render_template('event.html', event = event)


@app.route('/<event_token>/<driver_token>', methods = ['GET', 'POST'])
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
            return redirect(url_for('show_event', event_token=event_token))
        return render_template('show_driver.html', form = form)
    return False


@app.route('/<event_token>/add/<driver_type>', methods = ['GET', 'POST'])
def add_driver(event_token, driver_type):
    if driver_type == 'there':
        form = AddDriverThereForm()
        direction_boolean = True
    elif driver_type == 'back':
        form = AddDriverBackForm()
        direction_boolean = False
    else:
        return False
    event = Event.query.get(find(event_token))
    if form.validate_on_submit():
        driver = Driver(goingthere = direction_boolean, 
                        name = form.name.data,
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
    return render_template('add_driver.html', form = form)


@app.route('/<event_token>/<driver_token>/add', methods = ['GET', 'POST'])
def add_rider(event_token, driver_token):
    event = Event.query.get(find(event_token))
    driver = Driver.query.get(driver(event_token))
    if driver in event.drivers:
        form = AddRiderForm()
        if form.validate_on_submit():
            rider = Rider(name = form.name.data,
                          phone = form.phone.data)
            driver.riders.append(rider)
            db.session.add(rider)
            db.session.commit()
            return redirect(url_for('show_event', event_token = event_token))
        return render_template('add_rider.html', form = form, driver = driver)
    return False


#

if __name__ == '__main__':
    manager.run()

    