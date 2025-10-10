import pytest

from sandwich.core.service.llm import _extract_region
from sandwich.core.service.llm import get_claude_3_sonnet
from sandwich.core.service.llm import get_claude_sonnet_4_5
from sandwich.core.service.llm import get_gpt_oss


def test__extract_region():
    assert (
        _extract_region(
            "arn:aws:bedrock:ca-central-1:153784117502:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0"
        )
        == "ca-central-1"
    )
    assert _extract_region("global.anthropic.claude-sonnet-4-5-20250929-v1:0") is None
    assert _extract_region(None) is None


@pytest.mark.skip(reason="requires credentials")
def test_claude_3_sonnet():
    get_claude_3_sonnet().invoke("what is 1 + 1")


@pytest.mark.skip(reason="requires credentials")
def test_claude_sonnet_4_5():
    get_claude_sonnet_4_5().invoke("what is 1 + 1")


@pytest.mark.skip(reason="requires credentials")
def test_gpt_oss():
    get_gpt_oss().invoke("what is 1 + 1")
