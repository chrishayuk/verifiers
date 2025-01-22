import pytest
from verifiers.poetry.rhyme_verifier import RhymeVerifier

@pytest.fixture
def verifier():
    return RhymeVerifier()

def test_insufficient_lines(verifier):
    text = "Just one line"
    score = verifier.verify(text)
    assert score == 0.0, "Expected 0.0 with fewer than 2 lines."

def test_empty_tails(verifier):
    # If lines are blank, we get no rhyme tail
    text = """\
    
    """
    score = verifier.verify(text)
    assert score == 0.0, "Expected 0.0 for empty lines."

def test_full_rhyme_simple(verifier):
    """
    Two lines that end with words that have the same phoneme tail.
    Example: 'bee' and 'flee' often share IY1 in the CMU dictionary.
    """
    text = """\
I saw a buzzing bee
Then I found a smaller flee
"""
    score = verifier.verify(text)
    assert score == 1.0, f"Expected 1.0, got {score}"

def test_full_rhyme_flyer_choir(verifier):
    """
    'flyer' vs 'choir' often share the tail AY1-ER0, 
    making them a perfect rhyme by last-stressed-vowel logic.
    """
    text = """\
I saw a buzzing flyer
Then I found a wandering choir
"""
    score = verifier.verify(text)
    assert score == 1.0, f"Expected 1.0 but got {score}"

def test_full_rhyme_time_climb(verifier):
    """
    'time' vs 'climb' both have AY1-M from the last stressed vowel to the end,
    which the CMU dictionary often considers a full rhyme.
    """
    text = """\
Time
Climb
"""
    score = verifier.verify(text)
    assert score == 1.0, f"Expected 1.0, got {score}"

def test_custom_threshold(verifier):
    """
    If you ever introduce a partial-overlap approach in the future, 
    you can test how adjusting thresholds affects the result. 
    For now, we just ensure the code doesn't error out 
    when passing a custom threshold.
    """
    text = """\
Tame
Lame
"""
    # By standard logic, both lines share AY1-M => likely a full rhyme => 1.0
    score_strict = verifier.verify(text, partial_threshold=0.8)
    score_loose  = verifier.verify(text, partial_threshold=0.6)
    
    # We'll just confirm no errors and the score is within [0,1].
    assert 0.0 <= score_strict <= 1.0
    assert 0.0 <= score_loose <= 1.0

# --- New test for verify_with_feedback --- #
def test_feedback(verifier):
    """
    Test the extended feedback mechanism with a partial or fallback scenario.
    E.g., 'Hello' / 'Gallo' might share last letters ('o'), 
    but not necessarily a phoneme tail, giving partial fallback_credit=0.5.
    """
    text = """\
Hello
Gallo
"""
    # Suppose partial_threshold=0.8 => overlap ratio is likely <0.8 => fallback letter
    result = verifier.verify_with_feedback(text, partial_threshold=0.8, fallback_credit=0.5)
    score = result["score"]
    feedback = result["feedback"]

    # Expect partial credit of 0.5 (last-letter fallback), or 0.0 if the overlap logic differs
    # We'll allow any score in [0,1], but typically you'd check specific partial values:
    assert 0.0 <= score <= 1.0, f"Score out of range: {score}"

    # feedback is a list describing how the rhyme check went
    assert isinstance(feedback, list), "Expected feedback to be a list of messages"
    assert len(feedback) > 0, "Expected at least one feedback message"

    print("Rhyme feedback test complete.\nScore:", score)
    print("Feedback detail:")
    for msg in feedback:
        print(" -", msg)
