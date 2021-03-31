from src.redcap import Redcap, RedcapError
from src.enums import CodedValues
import requests
import pytest

session0_data = {'ash_id': 'ASH999',
                 'phone': '555-555-1234',
                 'value1_s0': '1',
                 'value2_s0': '2',
                 'value7_s0': '7',
                 'initials': 'ABC'}
session1_data = {'ash_id': 'ASH999',
                 'waketime': '07:00',
                 'sleeptime': '21:00',
                 'condition': '3'}


class TestRedcap:
    def test_get_participant_phone_invalid_id(self, requests_mock):
        rc = Redcap(api_token='test token')
        requests_mock.post(url=rc._endpoint,
                           status_code=requests.codes.ok,
                           json=[session0_data])

        with pytest.raises(RedcapError) as e:
            rc.get_participant_phone('Invalid ID')

        assert 'phone number' in str(e.value)

    def test_get_participant_phone_valid(self, requests_mock):
        rc = Redcap(api_token='test token')
        requests_mock.post(url=rc._endpoint,
                           status_code=requests.codes.ok,
                           json=[session0_data])

        post = rc.get_participant_phone('ASH999')

        assert post
        assert post == '555-555-1234'

    def test_get_participant_specific_data_invalid_id(self, requests_mock):
        session0_data.update(session1_data)

        rc = Redcap(api_token='test token')
        requests_mock.post(url=rc._endpoint,
                           status_code=requests.codes.ok,
                           json=[session0_data])

        with pytest.raises(RedcapError):
            rc.get_participant_specific_data('Invalid ID')

    def test_get_participant_specific_data_valid_id(self, requests_mock):
        session0_data.update(session1_data)

        rc = Redcap(api_token='test token')
        requests_mock.post(url=rc._endpoint,
                           status_code=requests.codes.ok,
                           json=[session0_data])

        part = rc.get_participant_specific_data('ASH999')

        assert part.participant_id == 'ASH999'
        assert part.message_values == [CodedValues.humor, CodedValues.relationships]
        assert part.task_values == [CodedValues.humor, CodedValues.athletic]

    def test_get_participant_specific_data_missing_session(self, requests_mock):
        # Test when session 1 is missing
        rc = Redcap(api_token='test token')
        requests_mock.post(rc._endpoint,
                           [
                               {'json': [session0_data], 'status_code': requests.codes.ok},
                               {'json': [], 'status_code': requests.codes.ok}
                           ])

        with pytest.raises(RedcapError) as e:
            rc.get_participant_specific_data('ASH999')

        assert 'session 1' in str(e.value)

    def test_get_participant_specific_data_does_not_follow_schema(self, requests_mock):
        rc = Redcap(api_token='test token')
        requests_mock.post(url=rc._endpoint,
                           status_code=requests.codes.ok,
                           json=[{'ash_id': 123}])

        with pytest.raises(RedcapError):
            rc.get_participant_specific_data('Response from REDCap')
