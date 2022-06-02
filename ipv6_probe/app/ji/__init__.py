from flask import Blueprint


ji = Blueprint('ji', __name__)

from . import views, errors