import copy
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from src.apptoto import Apptoto
from src.apptoto_event import ApptotoEvent
from src.apptoto_participant import ApptotoParticipant
from src.message import MessageLibrary
from src.participant import Participant

MESSAGES_PER_DAY_1 = 5
MESSAGES_PER_DAY_2 = 4


def intervals_valid(deltas: List[int]) -> bool:
    """
    Determine if intervals are valid

    :param deltas: A list of integer number of seconds
    :return: True if the interval between each consecutive pair of entries
    to deltas is greater than one hour.
    """
    one_hour = timedelta(seconds=3600)
    for a, b in zip(deltas, deltas[1:]):
        interval = timedelta(seconds=(b - a))
        if interval < one_hour:
            return False

    return True


def random_times(start: datetime, end: datetime, n: int) -> List[datetime]:
    """
    Create randomly spaced times between start and sleep_time.
    :param n:
    :param start: Start time
    :type start: datetime
    :param end: End time
    :type end: datetime
    :param n: Number of times to create
    :return: List of datetime
    """
    delta = end - start
    r = [random.randrange(int(delta.total_seconds())) for _ in range(n)]
    r.sort()

    while not intervals_valid(r):
        r = [random.randrange(int(delta.total_seconds())) for _ in range(n)]
        r.sort()

    times = [start + timedelta(seconds=x) for x in r]
    return times


class EventGenerator:
    def __init__(self, config: Dict[str, str], participant: Participant, start_date: str, instance_path: str):
        """
        Generate events for making text messages.

        :param start_date:
        :param config: A dictionary of configuration values
        :param participant: The participant who will receive messages
        :type participant: Participant
        """
        self._config = config
        self._participant = participant
        self._start_date_str = start_date
        self._path = Path(instance_path) / 'messages.csv'

    def generate(self):
        apptoto = Apptoto(api_token=self._config['apptoto_api_token'],
                          user=self._config['apptoto_user'])
        part = ApptotoParticipant(name=self._participant.participant_id, phone=self._participant.phone_number)

        events = []
        messages = MessageLibrary(path=self._path)
        num_required_messages = 28 * (MESSAGES_PER_DAY_1 + MESSAGES_PER_DAY_2)
        condition_messages = messages.get_messages_by_condition(self._participant.condition,
                                                                self._participant.values,
                                                                num_required_messages)

        s = datetime.strptime(f'{self._start_date_str} {self._participant.wake_time}', '%Y-%m-%d %H:%M')
        e = datetime.strptime(f'{self._start_date_str} {self._participant.sleep_time}', '%Y-%m-%d %H:%M')

        n = 0
        for days in range(28):
            delta = timedelta(days=days)
            start = s + delta
            end = e + delta
            # Get times each day to send messages
            # Send 5 messages a day for the first 28 days
            times_list = random_times(start, end, MESSAGES_PER_DAY_1)
            for t in times_list:
                try:
                    events.append(ApptotoEvent(calendar=self._config['apptoto_calendar'], title='RS SMS',
                                               start_time=t, end_time=t,
                                               content=condition_messages[n].message,
                                               participants=[copy.copy(part)]))
                    n = n + 1
                except KeyError as ke:
                    logging.getLogger().warning(f'Unable to create message from template because of '
                                                f'invalid placeholder: {str(ke)}')

        for days in range(28):
            delta = timedelta(days=days)
            start = s + delta
            end = e + delta
            # Get times each day to send messages
            # Send 4 messages a day for the first 28 days
            times_list = random_times(start, end, MESSAGES_PER_DAY_2)
            for t in times_list:
                try:
                    events.append(ApptotoEvent(calendar=self._config['apptoto_calendar'], title='RS SMS',
                                               start_time=t, end_time=t,
                                               content=condition_messages[n].message,
                                               participants=[copy.copy(part)]))
                    n = n + 1
                except KeyError as ke:
                    logging.getLogger().warning(f'Unable to create message from template because of '
                                                f'invalid placeholder: {str(ke)}')
        if len(events) > 0:
            apptoto.post_events(events)
