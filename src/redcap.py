from typing import Dict

import requests

from src.participant import Participant


class RedcapError(Exception):
    def __init__(self, message):
        self.message = message


class Redcap:
    """
    Interact with the REDCap API to collect participant information.
    """

    def __init__(self, api_token: str, endpoint: str = 'https://redcap.uoregon.edu/api/'):
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
                part.participant_id = id_
                part.phone_number = s0['phone']

        session1 = self._get_session1()
        for s1 in session1:
            id_ = s1['rs_id']
            if id_ == participant_id:
                part.wake_time = s1['waketime']
                part.sleep_time = s1['sleeptime']

        if len(session0) == 0 or len(session1) == 0:
            raise RedcapError(f'Unable to find participant in Redcap - participant ID - {participant_id}')

        return part

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
                        'events[0]': 'session_0_arm_1'}
        return self._make_request(request_data, 'phone number')

    def _get_session1(self):
        request_data = {'content': 'record',
                        'format': 'json',
                        'fields[0]': 'rs_id',
                        'fields[1]': 'waketime',
                        'fields[2]': 'sleeptime',
                        'events[0]': 'session_1_arm_1'}
        return self._make_request(request_data, 'wake time and sleep time')
