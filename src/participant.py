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
        self.initials = ''
        self.phone_number = phone
        self.wake_time = None
        self.sleep_time = None
        self.condition = None
        self.values = []
