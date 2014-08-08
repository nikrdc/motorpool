import os
from flask import Flask, render_template, redirect, session, redirect, \
				  url_for, abort, flash, g
from flask.ext.script import Manager, Shell
from itsdangerous import URLSafeSerializer
from flask.ext.wtf import Form
from wtforms import StringField, SelectMultipleField, IntegerField, \
                    SubmitField, PasswordField, widgets
from dateutil import parser
from wtforms.validators import Length, Required, Email, ValidationError, \
                               NumberRange
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.migrate import Migrate, MigrateCommand
from threading import Thread
from flask.ext.mail import Mail, Message
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import LoginManager, login_required, UserMixin, \
                            login_user, current_user


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'substitute key'
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

def make_shell_context():
    return dict(app=app, db=db, Event=Event, Driver=Driver, Rider=Rider)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return Event.query.get(id)


# Models

class Event(UserMixin, db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))

    drivers = db.relationship('Driver', backref='event', lazy='dynamic')

    def __repr__(self):
        return '<Event %r>' % self.name

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Driver(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    going_there = db.Column(db.Boolean) 
    name = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    email = db.Column(db.String(64))
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
    email = db.Column(db.String(64))

    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))

    def __repr__(self):
        return '<Rider %r>' % self.name


# Forms

class EventForm(Form):
    name = StringField('Event name', validators = [Required(message = 'An\
                       event name is required.')])
    password = PasswordField('Optional event password')
    submit = SubmitField('Create')


class LoginForm(Form):
    password = PasswordField('Event password')
    submit = SubmitField('Enter')


class DriverForm(Form):
    name = StringField('Name', validators = [Required(message = 'A name is \
                       required.')])
    phone = StringField('Phone number', validators = [Required(message = 'A \
                        phone number is required.')])
    email = StringField('Email address', validators = [Email(message = 'This \
                        email address is invalid.'), Required(message = 'An \
                        email address is required.')])
    capacity = IntegerField('Total car capacity (including driver)',
                            validators = [NumberRange(1, 10), Required( 
                            message = 'The car capacity is required.')])
    def validate_capacity(form, field):
        if hasattr(g, 'driver'):
            if field.data < len(g.driver.riders.all()) + 1:
                raise ValidationError('The capacity cannot be less than the \
                                      total of the riders and driver.')
    car_color = StringField('Car color', validators = [Required(message = 'A \
                            car color is required.')])
    make_model = StringField('Car make and model', 
                             validators = [Required(message = 'A car make and \
                             model is required.')])
    directions = SelectMultipleField(
        'Which direction(s) are you travelling in?',
        choices=[('driving_there', 'I am driving there'),
                 ('driving_back', 'I am driving back')],
        option_widget=widgets.CheckboxInput(),
        widget = widgets.ListWidget(prefix_label = False))
    leaving_from = StringField('Location leaving from')
    leaving_at = StringField('Time departing at')
    
    def validate_leaving_at(form, field):
        '''
        if field.data:
            if parser.parse(field.data) < datetime.now():
                raise ValidationError('Time travelling is not permitted (yet).\
                                       Please enter a time in the future.')
        '''
        try:
            parser.parse(field.data)
        except TypeError:
            raise ValidationError('This time format is not le cool. Try the \
                                  placeholder format.')

    going_to = StringField('Location going to')
    going_at = StringField('Time departing at')

    def validate_going_at(form, field):
        '''
        if field.data:
            if parser.parse(field.data) < datetime.now():
                raise ValidationError('Time travelling is not permitted (yet).\
                                       Please enter a time in the future.')
        '''
        try:
            parser.parse(field.data)
        except TypeError:
            raise ValidationError('This time format is not le cool. Try the \
                                  placeholder format.')

    submit = SubmitField('Submit')
    save = SubmitField('Save info')


class RiderForm(Form):
    name = StringField('Name', validators = [Required(message = 'A name is\
                       required.')])
    phone = StringField('Phone number', validators = [Required(message = 'A \
                        phone number is required.')])
    email = StringField('Email address', validators = [Email(message='This \
                        email address is invalid.')])
    submit = SubmitField('Submit')


# Email

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message('Motorpool: ' + subject, sender = 'Motorpool', 
                  recipients = [to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target = send_async_email, args = [app, msg])
    thr.start()
    return thr


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
                email = form.email.data,
                capacity = form.capacity.data,
                car_color = form.car_color.data,
                make_model = form.make_model.data,
                location = getattr(form, location_filler).data,
                datetime = parser.parse(getattr(form, datetime_filler).data),
                event = event)
    return driver 

def check_credentials(event):
    if event.password_hash:
        if current_user == event:
            return True
        else:
            return False
    else:
        return True


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
        if form.password.data:
            event = Event(name = form.name.data, password = form.password.data)
        else:
            event = Event(name = form.name.data)
        db.session.add(event)
        db.session.commit()
        login_user(event)
        event_token = generate_token(event)
        flash('Share this page\'s URL with other attendees!')
        return redirect(url_for('show_event', event_token = event_token))
    else:
        return render_template('index.html', form = form)


@app.route('/<event_token>/login', methods = ['GET', 'POST'])
def login(event_token):
    event = Event.query.get(find(event_token))
    if event:
        if check_credentials(event):
            return redirect(url_for('show_event', event_token = event_token))
        else:
            form = LoginForm()
            if form.validate_on_submit():
                if event.verify_password(form.password.data):
                    login_user(event)
                    return redirect(url_for('show_event', 
                                            event_token = event_token))
                else:
                    flash('This password is incorrect.')
                    return render_template('login.html', form = form)
            else:
                return render_template('login.html', form = form)    
    else:
        abort(404)


@app.route('/<event_token>')
def show_event(event_token):
    event = Event.query.get(find(event_token))
    if event:
        if check_credentials(event):
            rides_there = [driver for driver in event.drivers.all() if \
                           driver.going_there == True]
            rides_back = [driver for driver in event.drivers.all() if \
                          driver.going_there == False]
            return render_template('event.html', event = event, 
                                   event_token = event_token,
                                   rides_there = rides_there,
                                   rides_back = rides_back)
        else:
            return redirect(url_for('login', event_token = event_token))
    else:
        abort(404)


@app.route('/<event_token>/<driver_id>', methods = ['GET', 'POST'])
def show_driver(event_token, driver_id):
    event = Event.query.get(find(event_token))
    if event:
        if check_credentials(event):
            driver = Driver.query.get(driver_id)
            if driver in event.drivers:
                form = DriverForm(obj = driver, leaving_from = driver.location,
                leaving_at = driver.datetime.strftime('%B %-d %Y, %-I:%M %p'), 
                going_to = driver.location,
                going_at = driver.datetime.strftime('%B %-d %Y, %-I:%M %p'))
                g.driver = driver
                if form.validate_on_submit():
                    driver.name = form.name.data
                    driver.phone = form.phone.data
                    driver.email = form.email.data
                    driver.capacity = form.capacity.data
                    driver.car_color = form.car_color.data
                    driver.make_model = form.make_model.data
                    if driver.going_there:
                        driver.location = form.leaving_from.data
                        driver.datetime = parser.parse(form.leaving_at.data)
                    else:
                        driver.location = form.going_to.data
                        driver.datetime = parser.parse(form.going_at.data)
                    db.session.add(driver)
                    db.session.commit()
                    return redirect(url_for('show_event', 
                                            event_token = event_token))
                else:
                    return render_template('driver.html', 
                                           event_token = event_token,
                                           driver = driver, form = form)
            else:
                abort(404)
        else:
            return redirect(url_for('login', event_token = event_token))
    else:
        abort(404)


@app.route('/<event_token>/<driver_id>/delete', methods = ['POST'])
def delete_driver(event_token, driver_id):
    event = Event.query.get(find(event_token))
    driver = Driver.query.get(driver_id)
    if event and driver in event.drivers:
        db.session.delete(driver)
        send_email(driver.email, 'Your ride has been deleted', 
                   'mail/driver_deleted_driver', driver = driver, 
                   event = event)
        riders = driver.riders
        for rider in driver.riders:
            db.session.delete(rider)
            send_email(rider.email, 'A ride you were in has been deleted', 
                       'mail/driver_deleted_rider', rider = rider,
                       driver = driver, event = event)
        db.session.commit()
        return redirect(url_for('show_event', event_token = event_token))
    else:
        abort(404)


@app.route('/<event_token>/<driver_id>/<rider_id>/delete', methods = ['POST'])
def delete_rider(event_token, driver_id, rider_id):
    event = Event.query.get(find(event_token))
    driver = Driver.query.get(driver_id)
    rider = Rider.query.get(rider_id)
    if event and driver in event.drivers and rider in driver.riders:
        db.session.delete(rider)
        send_email(rider.email, 'You have been deleted from a ride', 
                   'mail/rider_deleted_rider', rider = rider,
                   driver = driver, event = event)
        db.session.commit()
        return redirect(url_for('show_driver', event_token = event_token,
                                driver_id = driver_id))
    else:
        abort(404)


@app.route('/<event_token>/add', methods = ['GET', 'POST'])
def add_driver(event_token):
    event = Event.query.get(find(event_token))
    if event:
        if check_credentials(event):
            form = DriverForm()
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
                    abort(500)
                db.session.commit()
                return redirect(url_for('show_event', event_token = event_token))
            else:
                return render_template('add_driver.html', form = form)
        else:
            return redirect(url_for('login', event_token = event_token))
    else:
        abort(404)


@app.route('/<event_token>/<driver_id>/add', methods = ['GET', 'POST'])
def add_rider(event_token, driver_id):
    event = Event.query.get(find(event_token))
    if event:
        if check_credentials(event):
            driver = Driver.query.get(driver_id)
            if driver in event.drivers:
                if len(driver.riders.all()) < driver.capacity - 1:
                    form = RiderForm()
                    if form.validate_on_submit():
                        rider = Rider(name = form.name.data,
                                      phone = form.phone.data,
                                      email = form.email.data,
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
                    return redirect(url_for('show_event', 
                                            event_token = event_token))
            else:
                abort(404)
        else:
            return redirect(url_for('login', event_token = event_token))
    else:
        abort(404)




if __name__ == '__main__':
    manager.run()

    