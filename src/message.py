import csv
from random import shuffle
from typing import List

from src.enums import Condition, CodedValues


class IndividualMessage:
    def __init__(self, random_id: int, message: str, condition: Condition, coded_values: CodedValues):
        """
        An individual message and its metadata.

        :param random_id: Random identifier of message
        :param message: The message text itself
        :param condition: The condition the message corresponds to
        :param coded_values: The values expressed in the message
        """
        self._id = random_id
        self.message = message
        self._condition = condition
        self._coded_values = coded_values

    @property
    def message_id(self):
        return self._id

    @property
    def condition(self):
        return self._condition

    @property
    def coded_value(self):
        return self._coded_values


class MessageLibrary:
    def __init__(self, path: str):
        """
        Read messages and associated metadata.

        :param path: File containing messages
        """
        self._messages = []
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                identifier = int(row['UO_ID'])
                condition = Condition(int(row['ConditionNo']))
                if condition == Condition.VALUES:
                    v = CodedValues[row['Value1']]
                else:
                    v = CodedValues.none

                m = IndividualMessage(random_id=identifier,
                                      message=row['Message'],
                                      condition=condition,
                                      coded_values=v)
                self._messages.append(m)

    def get_messages_by_condition(self, condition: Condition, values: List[CodedValues], num_messages)\
            -> List[IndividualMessage]:
        messages = []
        if condition is Condition.VALUES:
            messages = [m for m in self._messages if m.condition is Condition.VALUES and m.coded_value in values]
        else:
            messages = [m for m in self._messages if m.condition is condition]

        shuffle(messages)
        while len(messages) < num_messages:
            messages = messages + messages

        return messages[:num_messages]
