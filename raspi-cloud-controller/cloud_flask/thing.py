from flask import Blueprint
from flask import flash, g, render_template, request, redirect, url_for

from . import db
from .common import ensure_thing_belongs_to_user, load_logged_in_user, login_required

bp = Blueprint('thing', __name__, url_prefix='/thing')


@bp.before_app_request
def before_app_request():
    load_logged_in_user()


@bp.route('/')
@login_required
def thing_index():
    return redirect(url_for('thing.thing_list'))


@bp.route('/list')
@login_required
def thing_list():
    things = db.find_things_by_user_id(g.user['id'])
    return render_template('thing/list.html', things=things)


@bp.route('/view/<thing_id>')
@login_required
@ensure_thing_belongs_to_user
def thing_view(thing_id: int):
    g.thing_capabilities = db.find_thing_capabilities_by_id(thing_id)
    return render_template('thing/view.html')


@bp.route('/delete/<thing_id>', methods=['GET', 'POST'])
@login_required
@ensure_thing_belongs_to_user
def thing_delete(thing_id: int):
    if request.method == 'POST':  # TODO don't forget about validation
        db.delete_thing(thing_id)
        flash('Thing deleted')
        return redirect(url_for('thing.thing_list'))

    return render_template('thing/delete.html')


@bp.route('/edit/<thing_id>', methods=['GET', 'POST'])
@login_required
@ensure_thing_belongs_to_user
def thing_edit(thing_id: int):
    if request.method == 'POST':  # TODO don't forget about validation
        endpoint_id = request.form['endpoint_id']
        friendly_name = request.form['friendly_name']
        description = request.form['description']
        manufacturer_name = request.form['manufacturer_name']
        alexa_category_id = request.form['alexa_category']

        capability_list = request.form.getlist('alexa_capability')
        capability_props_list = map(
            lambda x: ', '.join(map(
                lambda y: y.strip(),
                x.split(',', ))),
            request.form.getlist('alexa_capability_properties'))

        alexa_capabilities_with_props = list(zip(capability_list, capability_props_list))

        db.update_thing(thing_id, endpoint_id, g.user['id'], friendly_name, description, manufacturer_name,
                        alexa_category_id, alexa_capabilities_with_props)

        return redirect(url_for('thing.thing_view', thing_id=thing_id))

    g.thing_capabilities = db.find_thing_capabilities_by_id(thing_id)
    alexa_categories = db.get_all_categories()
    alexa_capabilities = db.get_all_capabilities()
    return render_template('thing/edit.html', alexa_categories=alexa_categories, alexa_capabilities=alexa_capabilities)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def thing_add():
    if request.method == 'POST':  # TODO don't forget about validation
        endpoint_id = request.form['endpoint_id']
        friendly_name = request.form['friendly_name']
        description = request.form['description']
        manufacturer_name = request.form['manufacturer_name']
        alexa_category_id = request.form['alexa_category']

        capability_list = request.form.getlist('alexa_capability')
        capability_props_list = map(
            lambda x: ', '.join(map(
                lambda y: y.strip(),
                x.split(',', ))),
            request.form.getlist('alexa_capability_properties'))

        alexa_capabilities_with_props = list(zip(capability_list, capability_props_list))

        thing_id = db.create_thing(endpoint_id, g.user['id'], friendly_name, description, manufacturer_name,
                                   alexa_category_id, alexa_capabilities_with_props)

        return redirect(url_for('thing.thing_view', thing_id=thing_id))

    alexa_categories = db.get_all_categories()
    alexa_capabilities = db.get_all_capabilities()
    return render_template('thing/add.html', alexa_categories=alexa_categories, alexa_capabilities=alexa_capabilities)
