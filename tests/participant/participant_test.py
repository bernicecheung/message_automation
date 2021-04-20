import pytest

from src.participant import Participant


class TestParticipant:
    def test_invalid_session0_date(self):
        part = Participant()

        with pytest.raises(ValueError):
            part.daily_diary_time()

    def test_session0_date_saturday(self):
        part = Participant()
        # 2021-04-24 is a Saturday
        part.session0_date = '2021-04-24'
        part.sleep_time = '20:00'

        first_date = part.daily_diary_time()

        # first_date should be a Sunday
        assert first_date.weekday() == 6

    def test_session0_date_sunday(self):
        part = Participant()
        # 2021-04-25 is a Sunday
        part.session0_date = '2021-04-25'
        part.sleep_time = '20:00'

        first_date = part.daily_diary_time()

        # first_date should be a Wednesday
        assert first_date.weekday() == 2

    def test_session0_date_weekday(self):
        part = Participant()
        # 2021-04-27 is a Tuesday
        part.session0_date = '2021-04-27'
        part.sleep_time = '20:00'

        first_date = part.daily_diary_time()

        # first_date should be a Thursday
        assert first_date.weekday() == 3
