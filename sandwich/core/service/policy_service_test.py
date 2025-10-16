from sandwich.core.service.policy_service import PolicyService


def test_get_by_slug_found():
    """Should find English privacy notice."""
    lang_info = PolicyService.get_by_slug("privacy-notice")
    assert lang_info is not None
    assert lang_info.lang == "en"
    assert lang_info.label == "Thrive Privacy Notice"


def test_get_by_slug_found_fr():
    """Should find French privacy notice."""
    lang_info = PolicyService.get_by_slug("privacy-notice-fr")
    assert lang_info is not None
    assert lang_info.lang == "fr"
    assert lang_info.label == "Avis de confidentialité Thrive"


def test_get_by_slug_not_found():
    """Should return None for unknown slug."""
    lang_info = PolicyService.get_by_slug("not-a-real-slug")
    assert lang_info is None
