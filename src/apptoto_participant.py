class ApptotoParticipant:
    def __init__(self, name: str, phone: str, email: str = ''):
        """
        Create an ApptotoParticipant.

        An ApptotoParticipant represents a single participant on an ApptotoEvent.
        This participant will receive messages via email or phone.

        :param str name: Participant name
        :param str phone: Participant phone number
        :param str email: Participant email
        """
        self.name = name
        self.phone = phone
        self.email = email
