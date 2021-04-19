from typing import Dict

import jsonschema
import requests

from src.enums import Condition, CodedValues
from src.participant import Participant


class RedcapError(Exception):
    def __init__(self, message):
        """
        An exception for interactions with REDCap.

        :param message: A string describing the error
        """
        self.message = message


def _get_session0_schema() -> Dict:
    schema = {
        "$schema": "Session 0 schema",
        "definitions": {
            "session0": {
                 "type": "object",
                 "properties": {
                     "ash_id": {
                         "description": "Unique subject identifier",
                         "type": "string",
                         "minLength": 6,
                         "maxLength": 6,
                         "pattern": "^ASH[0-9]{3}$"
                     },
                     "phone": {
                         "description": "Subject phone number",
                         "type": "string"
                     },
                     "value1_s0": {
                         "description": "Subject's most important value defined in session 0",
                         "type": "string",
                         "minLength": 1,
                         "maxLength": 1,
                         "pattern": "^[0-9]{1}$"
                     },
                     "value2_s0": {
                         "description": "Subject's second most important value defined in session 0",
                         "type": "string",
                         "minLength": 1,
                         "maxLength": 1,
                         "pattern": "^[0-9]{1}$"
                     },
                     "value7_s0": {
                         "description": "Subject's least important value defined in session 0",
                         "type": "string",
                         "minLength": 1,
                         "maxLength": 1,
                         "pattern": "^[0-9]{1}$"
                     },
                     "initials": {
                         "description": "Subject initials",
                         "type": "string"
                     },
                     "quitdate": {
                         "description": "Quit date",
                         "type": "string"
                     },
                     "date_s0": {
                         "description": "Session 0 date",
                         "type": "string"
                     },
                     "redcap_event_name": {
                         "description": "REDCap event name",
                         "type": "string"
                     },
                 }
             }
        },
        "type": "array",
        "items": {"$ref": "#/definitions/session0"}
    }
    return schema


def _get_session1_schema() -> Dict:
    schema = {
        "$schema": "Session 1 schema",
        "definitions": {
            "session1": {
                 "type": "object",
                 "properties": {
                     "ash_id": {
                         "description": "Unique subject identifier",
                         "type": "string",
                         "minLength": 6,
                         "maxLength": 6,
                         "pattern": "^ASH[0-9]{3}$"
                     },
                     "waketime": {
                         "description": "Usual time subject wakes up",
                         "type": "string",
                         "pattern": "^[0-9]{2}:[0-9]{2}$"
                     },
                     "sleeptime": {
                         "description": "Usual time subject goes to sleep",
                         "type": "string",
                         "pattern": "^[0-9]{2}:[0-9]{2}$"
                     },
                     "condition": {
                         "description": "Experimental condition",
                         "type": "string",
                         "minLength": 1,
                         "maxLength": 1,
                         "pattern": "^[0-9]{1}$"
                     },
                     "redcap_event_name": {
                         "description": "REDCap event name",
                         "type": "string"
                     },
                 }
             }
        },
        "type": "array",
        "items": {"$ref": "#/definitions/session1"}
    }
    return schema


def _validate(json: str, schema: Dict):
    try:
        jsonschema.validate(json, schema)
    except (jsonschema.ValidationError, jsonschema.SchemaError) as e:
        raise RedcapError('Response from REDCap does not match expected format') from e


class Redcap:
    def __init__(self, api_token: str, endpoint: str = 'https://redcap.uoregon.edu/api/'):
        """
        Interact with the REDCap API to collect participant information.

        :param api_token: API token for the REDCap project
        :param endpoint: REDCap endpoint URI
        """
        self._endpoint = endpoint
        self._headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self._timeout = 15
        self._data = {'token': api_token}

    def get_participant_specific_data(self, participant_id: str) -> Participant:
        """
        Get participant phone number, usual wake time, and usual sleep time for participant_id.
        :param participant_id: The participant identifier in the form RSnnn
        :return: A Participant
        """
        part = Participant()

        session0 = self._get_session0()
        _validate(session0, _get_session0_schema())

        for s0 in session0:
            id_ = s0['ash_id']
            if id_ == participant_id:
                part.participant_id = participant_id
                part.initials = s0['initials']
                part.phone_number = s0['phone']
                part.message_values.append(CodedValues(int(s0['value1_s0'])))
                part.message_values.append(CodedValues(int(s0['value2_s0'])))

                part.task_values.append(CodedValues(int(s0['value1_s0'])))
                part.task_values.append(CodedValues(int(s0['value7_s0'])))
                break

        if part.participant_id != participant_id:
            raise RedcapError(f'Unable to find session 0 in Redcap - participant ID - {participant_id}')

        session1 = self._get_session1()
        _validate(session1, _get_session1_schema())

        if len(session1) > 0:
            for s1 in session1:
                id_ = s1['ash_id']
                if id_ == participant_id:
                    part.wake_time = s1['waketime']
                    part.sleep_time = s1['sleeptime']
                    part.condition = Condition(int(s1['condition']))
                    break

        if not part.wake_time:
            raise RedcapError(f'Unable to find session 1 in Redcap - participant ID - {participant_id}')

        return part

    def get_participant_phone(self, participant_id: str) -> str:
        phone_number = None
        session0 = self._get_session0()
        _validate(session0, _get_session0_schema())

        for s0 in session0:
            id_ = s0['ash_id']
            if id_ == participant_id:
                phone_number = s0['phone']

        if not phone_number:
            raise RedcapError(f'Unable to find phone number in Redcap - participant ID - {participant_id}')

        return phone_number

    def _make_request(self, request_data: Dict[str, str], fields_for_error: str):
        request_data.update(self._data)
        r = requests.post(url=self._endpoint, data=request_data, headers=self._headers, timeout=self._timeout)
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            raise RedcapError(f'Unable to get {fields_for_error} from Redcap - {str(r.status_code)}')

    def _get_session0(self):
        request_data = {'content': 'record',
                        'format': 'json',
                        'fields[0]': 'ash_id',
                        'fields[1]': 'phone',
                        'fields[2]': 'value1_s0',
                        'fields[3]': 'value2_s0',
                        'fields[4]': 'value7_s0',
                        'fields[5]': 'initials',
                        'fields[6]': 'quitdate',
                        'fields[7]': 'date_s0',
                        'events[0]': 'session_0_arm_1'}
        return self._make_request(request_data, 'Session 0 data')

    def _get_session1(self):
        request_data = {'content': 'record',
                        'format': 'json',
                        'fields[0]': 'ash_id',
                        'fields[1]': 'waketime',
                        'fields[2]': 'sleeptime',
                        'fields[3]': 'condition',
                        'events[0]': 'session_1_arm_1'}
        return self._make_request(request_data, 'Session 1 data')
