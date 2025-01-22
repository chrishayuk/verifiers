import pytest
from verifiers.poetry.haiku_verifier import HaikuVerifier

@pytest.fixture
def verifier():
    """Returns an instance of HaikuVerifier."""
    return HaikuVerifier()

def test_not_enough_lines(verifier):
    """Test that we get 0.0 for input with fewer than 3 lines."""
    text = """\
An old silent pond
A frog jumps in
"""
    score = verifier.verify(text)
    # Because there are only 2 lines, the verifier returns 0.0 immediately.
    assert score == 0.0, f"Expected 0.0 for fewer than 3 lines, got {score}"

def test_empty_text(verifier):
    """Test that empty or whitespace-only text also yields 0.0."""
    text = """   """
    score = verifier.verify(text)
    assert score == 0.0, f"Expected 0.0 for empty text, got {score}"

def test_perfect_haiku(verifier):
    """Test a classic haiku that should yield score = 1.0."""
    text = """\
An old silent pond
A frog jumps into the pond—
Splash! Silence again.
"""
    score = verifier.verify(text)
    assert score == 1.0, f"Expected 1.0, got {score}"

def test_two_correct_one_wrong(verifier):
    """
    If exactly 2 lines meet the 5/7/5 requirement, 
    the final score should be 2/3 (≈0.6667).
    """
    text = """\
Calmly falls the snow
Soft white upon the dark tree
Dancing bright with happiness
"""
    # Suppose line 3 has too many (or too few) syllables.
    score = verifier.verify(text)
    expected = pytest.approx(2/3, 0.001)
    assert score == expected, f"Expected {expected}, got {score}"

def test_wrong_structure(verifier):
    """
    3 lines, but none within the correct syllable range => 0.0 score.
    That means 0/3 lines are correct => 0.0 fraction.
    """
    text = """\
One
Two
Three
"""
    score = verifier.verify(text)
    assert score == 0.0, f"Expected 0.0, got {score}"

def test_custom_tolerance(verifier):
    """
    Demonstrate that higher tolerance can increase the score
    by allowing lines to pass even if they're off by ±2 instead of ±1.
    """
    text = """\
Under the warm sun
Restless ocean waves roar loud
A new day begins
"""
    score_default = verifier.verify(text)
    score_custom = verifier.verify(text, tolerance=2)
    # We just expect the custom (tolerance=2) score to be >= the default
    assert score_custom >= score_default, (
        f"Expected {score_custom} >= {score_default}"
    )

def test_feedback(verifier):
    """
    Check the 'verify_with_feedback' output with a 3-line poem 
    that fails at least one line's syllable check.
    """
    text = """\
A quiet fox runs
Through the bright snow in moonlight
Then vanishes soon
"""
    result = verifier.verify_with_feedback(text)
    score = result["score"]
    feedback_list = result["feedback"]

    # Score should be in [0,1]
    assert 0.0 <= score <= 1.0

    # We expect exactly 3 feedback messages (one per line)
    assert len(feedback_list) == 3, "We expect feedback for each line"

    # Example: check that line 2 feedback is present
    assert any("Line 2:" in msg for msg in feedback_list), "Expected feedback for line 2"

    print("Feedback test complete. Score:", score)
    print("Feedback details:")
    for f in feedback_list:
        print("-", f)
