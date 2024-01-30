from flask import Blueprint

bp = Blueprint('skills', __name__)


from app.skills import routes