from pathlib import Path

from hypothesis import given, strategies as st

from src.event_generator import MESSAGES_PER_DAY_1, MESSAGES_PER_DAY_2
from src.message import MessageLibrary
from src.enums import Condition, CodedValues


# Test that every combination of Condition and CodedValues has enough messages
@given(c=st.sampled_from(Condition),
       v=st.permutations(CodedValues).map(lambda x: x[:3]))
def test_enough_messages(c, v):
    shared_datadir = Path.cwd() / 'message' / 'data'
    messages = MessageLibrary(path=str(shared_datadir / 'messages.csv'))
    num_required_messages = 28 * (MESSAGES_PER_DAY_1 + MESSAGES_PER_DAY_2)

    condition_messages = messages.get_messages_by_condition(c, v, num_required_messages)

    assert len(condition_messages) >= num_required_messages
