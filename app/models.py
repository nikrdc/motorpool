from . import db
from itsdangerous import URLSafeSerializer

class User:
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))

    edit_serializer = URLSafeSerializer(current_app.config['SECRET_KEY'], 
                                        salt='edit')
    
    def generate_token(self, serializer):
        return serializer.dumps(self.id)

    def find(token, serializer):
        try:
            data = serializer.loads(token)
        except:
            return False
        return data


class Event(db.Model, User):
    __tablename__ = 'events'

    public_serializer = URLSafeSerializer(current_app.config['SECRET_KEY'], 
                                          salt='public')

    drivers = db.relationship('Driver', backref='event', lazy='dynamic')

    def __repr__(self):
        return '<Event %r>' % self.name


class Driver(db.Model, User):
    __tablename__ = 'drivers'

    phone = db.Column(db.String(64))
    goingthere = db.Column(db.Boolean) 
    capacity = db.Column(db.Integer)
    make_model = db.Column(db.String(64))
    car_color = db.Column(db.String(64))
    datetime = db.Column(db.DateTime)
    location = db.Column(db.String(64))

    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    riders = db.relationship('Rider', backref='driver', lazy='dynamic')

    def __repr__(self):
        return '<Driver %r>' % self.name


class Rider(db.Model, User):
    __tablename__ = 'riders'

    phone = db.Column(db.String(64))

    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'))

    def __repr__(self):
        return '<Rider %r>' % self.name

