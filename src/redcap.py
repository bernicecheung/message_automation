from typing import Dict, Optional

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


class Redcap:
    def __init__(self, api_token: str, endpoint: str = 'https://redcap.uoregon.edu/api/'):
        """
        Interact with the REDCap API to collect participant information.

        :param api_token: API token for the REDCap project
        :param endpoint: REDCap endpoint URI
        """
        self._endpoint = endpoint
        self._headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self._timeout = 5
        self._data = {'token': api_token}

    def get_participant_specific_data(self, participant_id: str) -> Participant:
        """
        Get participant phone number, usual wake time, and usual sleep time for participant_id.
        :param participant_id: The participant identifier in the form RSnnn
        :return: A Participant
        """
        part = Participant()

        session0 = self._get_session0()
        for s0 in session0:
            id_ = s0['rs_id']
            if id_ == participant_id:
                part.participant_id = participant_id
                part.initials = s0['initials']
                part.phone_number = s0['phone']
                part.values.append(CodedValues(int(s0['value1_s0'])))
                part.values.append(CodedValues(int(s0['value2_s0'])))
                part.values.append(CodedValues(int(s0['value3_s0'])))
                break

        session1 = self._get_session1()
        for s1 in session1:
            id_ = s1['rs_id']
            if id_ == participant_id:
                part.wake_time = s1['waketime']
                part.sleep_time = s1['sleeptime']
                part.condition = Condition(int(s1['condition']))
                break

        if part.participant_id != participant_id:
            raise RedcapError(f'Unable to find participant in Redcap - participant ID - {participant_id}')

        return part

    def get_participant_phone(self, participant_id: str) -> Optional[str]:
        phone_number = None
        session0 = self._get_phone()
        for s0 in session0:
            id_ = s0['rs_id']
            if id_ == participant_id:
                phone_number = s0['phone']

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
                        'fields[0]': 'rs_id',
                        'fields[1]': 'phone',
                        'fields[2]': 'value1_s0',
                        'fields[3]': 'value2_s0',
                        'fields[4]': 'value3_s0',
                        'fields[5]': 'initials',
                        'events[0]': 'session_0_arm_1'}
        return self._make_request(request_data, 'Session 0 data')

    def _get_session1(self):
        request_data = {'content': 'record',
                        'format': 'json',
                        'fields[0]': 'rs_id',
                        'fields[1]': 'waketime',
                        'fields[2]': 'sleeptime',
                        'fields[3]': 'condition',
                        'events[0]': 'session_1_arm_1'}
        return self._make_request(request_data, 'Session 1 data')

    def _get_phone(self):
        request_data = {'content': 'record',
                        'format': 'json',
                        'fields[0]': 'rs_id',
                        'fields[1]': 'phone',
                        'events[0]': 'session_0_arm_1'}
        return self._make_request(request_data, 'Phone number')
