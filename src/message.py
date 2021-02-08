import csv
from enum import Enum
from typing import List


class Condition(Enum):
    DOWNREG = 1
    HIGHLEVEL = 2
    VALUES = 3


class CodedValues(Enum):
    humor = 1
    relationships = 2
    creativity = 3
    achievement = 4
    religious = 5
    physical = 6
    athletic = 7
    none = 8


class IndividualMessage:
    def __init__(self, random_id: int, message: str, condition: Condition, coded_values: CodedValues):
        self._id = random_id
        self.message = message
        self._condition = condition
        self._coded_values = coded_values

    @property
    def condition(self):
        return self._condition

    @property
    def coded_value(self):
        return self._coded_values


class MessageLibrary:
    def __init__(self, path: str):
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

    def get_messages_by_condition(self, condition: Condition, values: List[CodedValues]) -> List[IndividualMessage]:
        if condition is Condition.VALUES:
            return [m for m in self._messages if m.condition is Condition.VALUES and m.coded_value in values]
        else:
            return [m for m in self._messages if m.condition is condition]
