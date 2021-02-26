from datetime import datetime
from typing import Optional, List

from flask import (
    Blueprint, current_app, flash, render_template, request, send_file
)
from werkzeug.datastructures import ImmutableMultiDict

from src.apptoto import Apptoto
from src.event_generator import EventGenerator
from src.redcap import Redcap, RedcapError

bp = Blueprint('blueprints', __name__)


def _validate_participant_id(form_data: ImmutableMultiDict) -> Optional[List[str]]:
    errors = []
    if len(form_data['participant']) != 5 or not form_data['participant'].startswith('RS'):
        errors.append('Participant identifier must be in form \"RSnnn\"')

    if errors:
        return errors
    else:
        return None


def _validate_form(form_data: ImmutableMultiDict) -> Optional[List[str]]:
    errors = []

    temp = _validate_participant_id(form_data)
    if temp is not None:
        errors += temp
    if len(form_data['start_date']) == 0:
        errors.append('Start date cannot be empty')

    if errors:
        return errors
    else:
        return None


@bp.route('/', methods=['GET', 'POST'])
def generation_form():
    if request.method == 'GET':
        return render_template('generation_form.html')
    elif request.method == 'POST':
        if 'submit' in request.form:
            # Access form properties and do stuff
            error = _validate_form(request.form)
            if error:
                for e in error:
                    flash(e, 'danger')
                return render_template('generation_form.html')

            rc = Redcap(api_token=current_app.config['AUTOMATIONCONFIG']['redcap_api_token'])
            try:
                part = rc.get_participant_specific_data(request.form['participant'])
            except RedcapError as err:
                flash(str(err), 'danger')
                return render_template('generation_form.html')

            eg = EventGenerator(config=current_app.config['AUTOMATIONCONFIG'], participant=part,
                                instance_path=current_app.instance_path)
            if eg.generate(request.form['start_date']):
                f = eg.write_file()
                return send_file(f, mimetype='text/csv', as_attachment=True)
            else:
                flash('Failed to create some messages', 'danger')
            return render_template('generation_form.html')


@bp.route('/delete', methods=['GET', 'POST'])
def delete_events():
    if request.method == 'GET':
        return render_template('delete_form.html')
    elif request.method == 'POST':
        if 'submit' in request.form:
            # Access form properties, get participant information, get events, and delete
            participant_id = request.form['participant']
            rc = Redcap(api_token=current_app.config['AUTOMATIONCONFIG']['redcap_api_token'])

            try:
                phone_number = rc.get_participant_phone(participant_id)
            except RedcapError as err:
                flash(str(err), 'danger')
                return render_template('delete_form.html')

            apptoto = Apptoto(api_token=current_app.config['AUTOMATIONCONFIG']['apptoto_api_token'],
                              user=current_app.config['AUTOMATIONCONFIG']['apptoto_user'])

            begin = datetime.now()
            event_ids = apptoto.get_events(begin=begin, phone_number=phone_number)
            for event_id in event_ids:
                apptoto.delete_event(event_id)

            flash('Deleted messages', 'success')
            return render_template('delete_form.html')


@bp.route('/task', methods=['GET', 'POST'])
def task():
    if request.method == 'GET':
        return render_template('task_form.html')
    elif request.method == 'POST':
        if 'value-task' in request.form:
            error = _validate_participant_id(request.form)
            if error:
                for e in error:
                    flash(e, 'danger')
                return render_template('task_form.html')

            rc = Redcap(api_token=current_app.config['AUTOMATIONCONFIG']['redcap_api_token'])
            try:
                part = rc.get_participant_specific_data(request.form['participant'])
            except RedcapError as err:
                flash(str(err), 'danger')
                return render_template('task_form.html')

            eg = EventGenerator(config=current_app.config['AUTOMATIONCONFIG'], participant=part,
                                instance_path=current_app.instance_path)

            f = eg.task_input_file()
            return send_file(f, mimetype='text/csv', as_attachment=True)
