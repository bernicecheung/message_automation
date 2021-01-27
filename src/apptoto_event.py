from datetime import datetime
from typing import List

from src.apptoto_participant import ApptotoParticipant


class ApptotoEvent:
    def __init__(self, calendar: str, title: str, start_time: datetime, end_time: datetime,
                 content: str, participants: List[ApptotoParticipant]):
        """
        Create an ApptotoEvent.

        An ApptotoEvent represents a single event.
        Messages will be sent at `start_time` to all `participants`.

        :param str calendar: Calendar name
        :param str title: Event title
        :param datetime start_time: Start time of event
        :param datetime end_time: End time of event
        :param str content: Message content about event
        :param List[ApptotoParticipants] participants: Participants who will receive message content
        """
        self.calendar = calendar
        self.title = title
        self.start_time = start_time.isoformat()
        self.end_time = end_time.isoformat()
        self.content = content
        self.participants = participants
