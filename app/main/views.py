from flask import render_template, redirect, url_for, abort, flash
from .forms import EventForm, DriverForm, RiderForm
from ..models import Event, Driver, Rider
from . import main
from .. import db


edit_serializer = URLSafeSerializer(current_app.config['SECRET_KEY'], 
                                        salt='edit')

public_serializer = URLSafeSerializer(current_app.config['SECRET_KEY'], 
                                          salt='public')

def generate_token(self, serializer):
    return serializer.dumps(self.id)

def find(token, serializer):
    try:
        data = serializer.loads(token)
    except:
        return False
    return data


@main.route('/', methods=['GET', 'POST'])
def index():


@main.route('/<event_public_token>')
def show_event(event_public_token):


@main.route('/<event_public_token>/join/<type>', methods=['GET', 'POST'])
def join(event_public_token, type):


@main.route('/edit/<event_edit_token>', methods=['GET', 'POST'])
def edit_event(event_edit_token):


@main.route('/<event_public_token>/edit/<type>/<type_token>', 
			methods=['GET', 'POST'])
def edit_participant(event_public_token, type, type_token):

