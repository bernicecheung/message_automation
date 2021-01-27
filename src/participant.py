from datetime import datetime


class Participant:
    def __init__(self, identifier: str = '', phone: str = ''):
        """
        A single participant to the study, that will receive messages

        :param identifier: The participant identifier, in the format RS%3d (RS followed by three digits)
        :type identifier: str
        :param phone: Phone number
        :type phone: str
        """
        self.participant_id = identifier
        self.phone_number = phone
        self._wake_time = None
        self._sleep_time = None

    @property
    def wake_time(self):
        return self._wake_time

    @wake_time.setter
    def wake_time(self, value):
        self._wake_time = datetime.strptime(value, '%H:%M')

    @property
    def sleep_time(self):
        return self._wake_time

    @sleep_time.setter
    def sleep_time(self, value):
        self._sleep_time = datetime.strptime(value, '%H:%M')