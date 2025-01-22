import pytest
from verifiers.poetry.tanka_verifier import TankaVerifier

@pytest.fixture
def verifier():
    """Returns an instance of TankaVerifier."""
    return TankaVerifier()

def test_not_enough_lines(verifier):
    """Test that we get 0.0 for input with fewer than 5 lines."""
    text = """\
Line one
Line two
Line three
Line four
"""
    score = verifier.verify(text)
    assert score == 0.0, f"Expected 0.0 for fewer than 5 lines, got {score}"

def test_empty_text(verifier):
    """Test that empty or whitespace-only text also yields 0.0."""
    text = """   """
    score = verifier.verify(text)
    assert score == 0.0, f"Expected 0.0 for empty text, got {score}"

def test_perfect_tanka(verifier):
    """Test a 5-line poem with ~5-7-5-7-7 syllables yields score=1.0."""
    # A naive English example; approximate syllables:
    text = """\
In silent evening
Fireflies float across the pond
Soft wings shimmering
Autumn breeze whispers gently
Dreams linger beneath the moon
"""
    score = verifier.verify(text)
    assert score == 1.0, f"Expected 1.0, got {score}"

def test_two_correct_three_wrong(verifier):
    """
    If exactly 2 lines meet their target, 
    final score should be 2/5 = 0.4.
    """
    text = """\
Quiet star rises
Ocean waves carry softly
Mismatch line
Mismatch again
Mismatch yet again
"""
    score = verifier.verify(text)
    expected = pytest.approx(0.4, 0.001)
    assert score == expected, f"Expected {expected}, got {score}"


def test_wrong_structure(verifier):
    """
    5 lines, but none within the correct syllable range => 0.0 score (0/5).
    """
    text = """\
One
Two
Three
Four
Five
"""
    score = verifier.verify(text)
    assert score == 0.0, f"Expected 0.0, got {score}"

def test_custom_tolerance(verifier):
    """
    Show that a higher tolerance can increase or maintain the score.
    If lines are borderline, a bigger tolerance might push them into range.
    """
    text = """\
A quiet fox leaps
Over the sunlit forest
Then recedes away
Winds carry silent echoes
Footprints whisper memories
"""
    score_default = verifier.verify(text)
    score_custom = verifier.verify(text, tolerance=2)
    # We just expect the custom (tolerance=2) score >= default
    assert score_custom >= score_default, (
        f"Expected score_custom >= score_default, got {score_custom} < {score_default}"
    )

def test_feedback(verifier):
    """
    Check the feedback structure with a partial tanka.
    If line count==5, we get 5 feedback messages (one per line).
    """
    text = """\
Night falls softly now
Stars wink across the wide sky
Melodies echo
This line may be too short
And final line grows longer
"""
    result = verifier.verify_with_feedback(text)
    score = result["score"]
    feedback_list = result["feedback"]

    # Score in [0,1]
    assert 0.0 <= score <= 1.0, f"Score out of range: {score}"

    # We expect exactly 5 feedback lines if line_count=5
    assert len(feedback_list) == 5, "Expected feedback for each of the 5 lines"

    # (Optional) Check specific line references in feedback
    # e.g., "Line 4" or "Line 5" mention "too short" or "too long" if out of range

    print("Feedback test complete. Score:", score)
    print("Feedback details:")
    for fmsg in feedback_list:
        print(" -", fmsg)
