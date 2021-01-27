import logging
from typing import List

import jsonpickle
import requests
from requests.auth import HTTPBasicAuth

from src.apptoto_event import ApptotoEvent


class Apptoto:
    def __init__(self, api_token: str, user: str):
        """
        Create an Apptoto instance.

        :param api_token: Apptoto API token
        :param user: Apptoto user name
        """
        self._endpoint = 'https://api.apptoto.com/v1'
        self._api_token = api_token
        self._user = user
        self._headers = {'Content-Type': 'application/json'}
        self._timeout = 5

    def post_events(self, events: List[ApptotoEvent]):
        """
        Post events to the /v1/events API to create events that will send messages to all participants.

        :param events: List of events to create
        """
        url = f'{self._endpoint}/events'
        request_data = jsonpickle.encode({'events': events, 'prevent_calendar_creation': True}, unpicklable=False)
        logging.getLogger().info('Posting events to apptoto')
        r = requests.post(url=url,
                          data=request_data,
                          headers=self._headers,
                          timeout=self._timeout,
                          auth=HTTPBasicAuth(username=self._user, password=self._api_token))

        if r.status_code == requests.codes.ok:
            logging.getLogger().info('Posted events to apptoto')
        else:
            logging.getLogger().info(f'Failed to post events - {str(r.status_code)} - {str(r.content)}')

        return r.status_code == requests.codes.ok
