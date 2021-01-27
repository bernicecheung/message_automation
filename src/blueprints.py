from typing import Optional, List

from flask import (
    Blueprint, current_app, flash, render_template, request
)
from werkzeug.datastructures import ImmutableMultiDict

from src.event_generator import EventGenerator
from src.redcap import Redcap, RedcapError

bp = Blueprint('blueprints', __name__)


def _validate_form(form_data: ImmutableMultiDict) -> Optional[List[str]]:
    errors = []
    if len(form_data['participant']) != 5 or not form_data['participant'].startswith('RS'):
        errors.append('Participant identifier must be in form \"RSnnn\"')
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

            eg = EventGenerator(config=current_app.config['AUTOMATIONCONFIG'], participant=part)
            eg.generate()

            flash('Successfully generated messages', 'success')
            return render_template('generation_form.html')
