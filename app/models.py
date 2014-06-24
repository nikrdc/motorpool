from . import db


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    drivers = db.relationship('Driver', backref='event', lazy='dynamic')

    def __repr__(self):
        return '<Event %r>' % self.name


class User(db.Model):
    __tablename__ = 'drivers'
    id = db.Column(db.Integer, primary_key=True)
    direction = db.Columb(db.Boolean)
    name = db.Column(db.String(64))
    phone = db.Column(db.String(64))
    email = db.Column(db.String(64))
    capacity = db.Column(db.Integer)
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
    email = db.Column(db.String(64))

    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))

    def __repr__(self):
        return '<Rider %r>' % self.name