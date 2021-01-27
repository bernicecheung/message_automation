import copy
import logging
import random
from datetime import datetime, timedelta
from typing import Dict
from typing import List

from src.apptoto import Apptoto
from src.apptoto_event import ApptotoEvent
from src.apptoto_participant import ApptotoParticipant
from src.participant import Participant


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
    """
    Generate events for making text messages
    """

    def __init__(self, config: Dict[str, str], participant: Participant):
        self._config = config
        self._participant = participant

    def generate(self):
        apptoto = Apptoto(api_token=self._config['apptoto_api_token'],
                          user=self._config['apptoto_user'])
        part = ApptotoParticipant(name=self._participant.participant_id, phone=self._participant.phone_number)

        # TODO: Read in list of value strings
        # TODO: Generate messages for each day. Send 5 messages per day for the first 28 days (4 weeks),
        #       then send 4 messages per day for the next 28 days (4 weeks).
        events = []

        # Get times each day to send messages
        times_list = random_times(self._participant.wake_time, self._participant.sleep_time, 5)

        for i, t in enumerate(times_list, start=1):
            try:
                events.append(ApptotoEvent(calendar=self._config['apptoto_calendar'], title=f'Message {i}',
                                           start_time=t, end_time=t,
                                           content=f'Smoking study message content. Message number {i}',
                                           participants=[copy.copy(part)]))
            except KeyError as ke:
                logging.getLogger().warning(f'Unable to create message from template because of '
                                            f'invalid placeholder: {str(ke)}')
        if len(events) > 0:
            apptoto.post_events(events)
