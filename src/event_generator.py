import copy
import csv
import logging
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from src.apptoto import Apptoto
from src.apptoto_event import ApptotoEvent
from src.apptoto_participant import ApptotoParticipant
from src.enums import Condition
from src.message import MessageLibrary
from src.participant import Participant

MESSAGES_PER_DAY_1 = 5
MESSAGES_PER_DAY_2 = 4
DAYS = 28
TASK_MESSAGES = 64
ITI = [
    1.8,
    4.5,
    2.3,
    1.0,
    4.3,
    4.3,
    2.7,
    1.6,
    4.0,
    1.4,
    3.6,
    1.0,
    2.3,
    5.5,
    1.8,
    3.2,
    3.9,
    2.4,
    5.0,
    3.0,
    5.2,
    1.0,
    1.6,
    3.9,
    3.0,
    3.1,
    4.4,
    3.1,
    4.5,
    1.5,
    1.8,
    1.2,
    1.0,
    1.6,
    1.0,
    4.7,
    1.1,
    4.5,
    3.1,
    1.1,
    2.1,
    2.4,
    2.7,
    4.1,
    5.9,
    1.4,
    3.2,
    4.6,
    3.4,
    1.0,
    3.0,
    5.3,
    4.4,
    1.4,
    4.1,
    2.3,
    5.1,
    1.5,
    2.1,
    4.3,
    2.5,
    6.0,
    1.8,
    5.4
]


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
    def __init__(self, config: Dict[str, str], participant: Participant, instance_path: str):
        """
        Generate events for making text messages.

        :param config: A dictionary of configuration values
        :param participant: The participant who will receive messages
        :type participant: Participant
        """
        self._config = config
        self._participant = participant
        self._path = Path(instance_path) / config['message_file']
        self._messages = None

    def generate(self, start_date: str) -> bool:
        apptoto = Apptoto(api_token=self._config['apptoto_api_token'],
                          user=self._config['apptoto_user'])
        part = ApptotoParticipant(name=self._participant.initials, phone=self._participant.phone_number)

        events = []
        messages = MessageLibrary(path=self._path)
        num_required_messages = 28 * (MESSAGES_PER_DAY_1 + MESSAGES_PER_DAY_2)
        self._messages = messages.get_messages_by_condition(self._participant.condition,
                                                            self._participant.message_values,
                                                            num_required_messages)

        s = datetime.strptime(f'{start_date} {self._participant.wake_time}', '%Y-%m-%d %H:%M')
        e = datetime.strptime(f'{start_date} {self._participant.sleep_time}', '%Y-%m-%d %H:%M')
        hour_before_sleep_time = e - timedelta(seconds=3600)

        n = 0
        for days in range(DAYS):
            delta = timedelta(days=days)
            start = s + delta
            end = e + delta
            # Get times each day to send messages
            # Send 5 messages a day for the first 28 days
            times_list = random_times(start, end, MESSAGES_PER_DAY_1)
            for t in times_list:
                # Prepend each message with "UO: "
                content = "UO: " + self._messages[n].message
                events.append(ApptotoEvent(calendar=self._config['apptoto_calendar'],
                                           title='RS SMS',
                                           start_time=t,
                                           end_time=t,
                                           content=content,
                                           participants=[copy.copy(part)]))
                n = n + 1

        for days in range(DAYS, DAYS + DAYS):
            delta = timedelta(days=days)
            start = s + delta
            end = e + delta
            # Get times each day to send messages
            # Send 4 messages a day for the first 28 days
            times_list = random_times(start, end, MESSAGES_PER_DAY_2)
            for t in times_list:
                # Prepend each message with "UO: "
                content = "UO: " + self._messages[n].message
                events.append(ApptotoEvent(calendar=self._config['apptoto_calendar'],
                                           title='RS SMS',
                                           start_time=t,
                                           end_time=t,
                                           content=content,
                                           participants=[copy.copy(part)]))
                n = n + 1

        # Add one message per day asking for a reply with the number of cigarettes smoked
        for days in range(DAYS + DAYS):
            delta = timedelta(days=days)
            t = hour_before_sleep_time + delta
            content = "UO: Reply back with the number of cigarettes smoked today"
            events.append(ApptotoEvent(calendar=self._config['apptoto_calendar'],
                                       title='RS SMS',
                                       start_time=t,
                                       end_time=t,
                                       content=content,
                                       participants=[copy.copy(part)]))

        if len(events) > 0:
            return apptoto.post_events(events)

    def write_file(self):
        f = Path.home() / (self._participant.participant_id + '.csv')
        with open(f, 'w', newline='') as csvfile:
            fieldnames = ['UO_ID', 'Message']
            filewriter = csv.DictWriter(csvfile,
                                        delimiter=',',
                                        quotechar='\"',
                                        quoting=csv.QUOTE_MINIMAL,
                                        fieldnames=fieldnames)
            filewriter.writeheader()
            for m in self._messages:
                filewriter.writerow({'UO_ID': m.message_id, 'Message': m.message})

        return f

    def task_input_file(self):
        f = Path.home() / (self._participant.participant_id + '_conditions.csv')

        messages = MessageLibrary(path=self._path)
        num_required_messages = TASK_MESSAGES
        task_messages = messages.get_messages_by_condition(Condition.VALUES,
                                                           self._participant.task_values,
                                                           num_required_messages)
        with open(f, 'w', newline='') as csvfile:
            fieldnames = ['message', 'iti']
            filewriter = csv.DictWriter(csvfile,
                                        delimiter=',',
                                        quotechar='\"',
                                        quoting=csv.QUOTE_MINIMAL,
                                        fieldnames=fieldnames)
            filewriter.writeheader()
            for i, m in enumerate(task_messages):
                filewriter.writerow({fieldnames[0]: m.message, fieldnames[1]: ITI[i]})

        return f
