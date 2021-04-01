import logging
from datetime import datetime
from typing import List

import jsonpickle
import requests
from requests.auth import HTTPBasicAuth

from src.apptoto_event import ApptotoEvent
from src.constants import DAYS_1, DAYS_2, MESSAGES_PER_DAY_1, MESSAGES_PER_DAY_2


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
        self._timeout = 30

    def post_events(self, events: List[ApptotoEvent]):
        """
        Post events to the /v1/events API to create events that will send messages to all participants.

        :param events: List of events to create
        """
        url = f'{self._endpoint}/events'
        # Post 5 events at a time because Apptoto's API can't handle all events at once.
        for i in range(0, len(events), 5):
            events_slice = events[i:i + 5]
            request_data = jsonpickle.encode({'events': events_slice, 'prevent_calendar_creation': True}, unpicklable=False)
            print('Posting events to apptoto')
            r = requests.post(url=url,
                              data=request_data,
                              headers=self._headers,
                              timeout=self._timeout,
                              auth=HTTPBasicAuth(username=self._user, password=self._api_token))

            if r.status_code == requests.codes.ok:
                print('Posted events to apptoto')
            else:
                print(f'Failed to post events {i} through {i+5}, starting at {events[i].start_time}')
                print(f'Failed to post events - {str(r.status_code)} - {str(r.content)}')
                return r.status_code == requests.codes.ok

        return True

    def get_events(self, begin: datetime, phone_number: str) -> List[int]:
        url = f'{self._endpoint}/events'
        max_events = DAYS_1 * MESSAGES_PER_DAY_1 + DAYS_2 * MESSAGES_PER_DAY_2 + DAYS_1 + DAYS_2
        params = {'begin': begin.isoformat(),
                  'phone_number': phone_number,
                  'page_size': max_events}
        r = requests.get(url=url,
                         params=params,
                         headers=self._headers,
                         timeout=self._timeout,
                         auth=HTTPBasicAuth(username=self._user, password=self._api_token))

        event_ids = []
        if r.status_code == requests.codes.ok:
            events = r.json()['events']
            for e in events:
                event_ids.append(e['id'])
        else:
            print(f'Failed to get events - {str(r.status_code)} - {str(r.content)}')

        return event_ids

    def delete_event(self, event_id: int):
        url = f'{self._endpoint}/events'
        params = {'id': event_id}
        r = requests.delete(url=url,
                            params=params,
                            headers=self._headers,
                            timeout=self._timeout,
                            auth=HTTPBasicAuth(username=self._user, password=self._api_token))

        if r.status_code == requests.codes.ok:
            print(f'Deleted event - {event_id}')
