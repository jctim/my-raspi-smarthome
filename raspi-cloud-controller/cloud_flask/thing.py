from flask import Blueprint
from flask import (g, render_template)

from . import db
from .common import (ensure_thing_belongs_to_user, load_logged_in_user,
                     login_required)

bp = Blueprint('thing', __name__, url_prefix='/thing')


@bp.before_app_request
def before_app_request():
    load_logged_in_user()


@bp.route('/list')
@login_required
def list():
    things = db.find_things_by_user_id(g.user['id'])
    return render_template('thing/list.html', things=things)


@bp.route('/view/<thing_id>')
@login_required
@ensure_thing_belongs_to_user
def view(thing_id: int):
    g.thing_capabilities = db.find_thing_capabilities_by_id(g.user['id'])
    return render_template('thing/view.html')


@bp.route('/edit/<thing_id>')
@login_required
@ensure_thing_belongs_to_user
def edit(thing_id: int):
    # TODO: process POST 
    g.thing_capabilities = db.find_thing_capabilities_by_id(g.user['id'])
    alexa_categories = db.get_all_categories()
    alexa_capabilities = db.get_all_capabilities()
    return render_template('thing/edit.html', alexa_categories=alexa_categories, alexa_capabilities=alexa_capabilities)


@bp.route('/add')
@login_required
def add():
    # TODO: process POST 
    alexa_categories = db.get_all_categories()
    alexa_capabilities = db.get_all_capabilities()
    return render_template('thing/add.html', alexa_categories=alexa_categories, alexa_capabilities=alexa_capabilities)
