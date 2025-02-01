import pytest
from verifiers.poetry.rhyme_verifier import RhymeVerifier

@pytest.fixture
def verifier():
    """Returns an instance of RhymeVerifier."""
    return RhymeVerifier()

def test_insufficient_lines(verifier):
    """
    If fewer than 2 lines are provided => 0.0 score,
    and feedback should mention 'Need at least 2 lines'.
    """
    text = "Just one line"
    result = verifier.verify_with_feedback(text)
    score = result["score"]
    feedback = result["feedback"]
    assert score == 0.0, f"Expected 0.0, got {score}"
    assert any("Need at least 2 lines" in msg for msg in feedback), (
        "Expected feedback indicating insufficient lines."
    )

def test_perfect_rhyme(verifier):
    """
    Two lines that share the same final phonetic chunk => 1.0.
    Check that feedback mentions 'Perfect rhyme'.
    """
    text = """\
I love my cat
He sat on the mat
"""
    result = verifier.verify_with_feedback(text)
    score = result["score"]
    feedback = result["feedback"]
    assert score == 1.0, f"Expected perfect rhyme => 1.0, got {score}"
    assert any("Perfect rhyme" in msg for msg in feedback), (
        "Expected feedback mentioning 'Perfect rhyme'."
    )

def test_partial_rhyme(verifier):
    """
    Overlap ratio meets threshold => partial credit.
    We want to ensure it's neither 0.0 nor 1.0, but somewhere in between.
    """
    text = """\
My voice was bold
Your choice was held
"""
    result = verifier.verify_with_feedback(text)
    score = result["score"]
    feedback = result["feedback"]

    # By default partial_threshold=0.5
    # Overlap ratio should be >=0.5 but <1.0 => partial credit.
    # We'll just assert 0.0 < score < 1.0.
    assert 0.0 < score < 1.0, f"Expected partial rhyme credit, got {score}"
    # Check overlap ratio is mentioned
    assert any("Overlap ratio:" in msg for msg in feedback), (
        "Expected feedback with 'Overlap ratio: ...'"
    )
    # Check that partial overlap mention is there
    assert any("partial rhyme credit" in msg for msg in feedback), (
        "Expected 'partial rhyme credit' in feedback"
    )

def test_last_letter_fallback(verifier):
    """
    If phonetic overlap fails but last letters match, fallback_credit is awarded.
    Check that the feedback references 'Last letters match'.
    """
    text = """\
I love my orange bap
He leaps around with a cup
"""
    result = verifier.verify_with_feedback(text)
    score = result["score"]
    feedback = result["feedback"]

    # Expect insufficient phonetic overlap => fallback => default 0.5
    assert score == 0.5, f"Expected fallback credit=0.5, got {score}"
    assert any("Last letters match" in msg for msg in feedback), (
        "Expected feedback referencing last-letter fallback."
    )


def test_no_rhyme(verifier):
    """
    If there's no phonetic overlap and no last-letter match => 0.0.
    """
    text = """\
Hello
World
"""
    result = verifier.verify_with_feedback(text)
    score = result["score"]
    feedback = result["feedback"]
    assert score == 0.0, f"Expected 0.0, got {score}"
    assert any("No letter match" in msg for msg in feedback), (
        "Expected 'No letter match' fallback in feedback, got something else."
    )

def test_custom_threshold_and_credit(verifier):
    """
    Using partial_threshold=0.8, fallback_credit=0.2.
    We want an overlap <0.8 so we end up with fallback=0.2.
    """
    text = """\
I poured some fresh milk
He prayed like a monk
"""
    result = verifier.verify_with_feedback(
        text,
        partial_threshold=0.8,
        fallback_credit=0.2
    )
    score = result["score"]
    feedback = result["feedback"]

    # Expect overlap ratio <0.8 => fallback => 0.2
    assert score == 0.2, f"Expected fallback credit=0.2, got {score}"

    # Confirm we see threshold mention
    assert any("(threshold=0.8)" in msg for msg in feedback), (
        "Expected mention of the custom threshold=0.8."
    )
    # Confirm fallback mention
    assert any("Last letters match" in msg for msg in feedback), (
        "Expected a fallback mention for the last-letter match."
    )


def test_line_breakdown_in_feedback(verifier):
    """
    Verify that the updated RhymeVerifier provides per-line breakdown info
    (words, syllables, breakdown) in the feedback.
    """
    text = """\
Silly goose
Thrilling noose
"""
    result = verifier.verify_with_feedback(text)
    score = result["score"]
    feedback = result["feedback"]

    # The first two feedback entries should reference "Line 1 (..)" and "Line 2 (..)"
    # with words, syllables, etc.
    assert any("Line 1 (" in msg for msg in feedback), "Expected line 1 breakdown in feedback."
    assert any("Line 2 (" in msg for msg in feedback), "Expected line 2 breakdown in feedback."
    assert any("Words:" in msg for msg in feedback), "Expected 'Words:' in feedback."
    assert any("Syllables per word:" in msg for msg in feedback), "Expected 'Syllables per word:' in feedback."
    assert any("Syllable breakdown:" in msg for msg in feedback), "Expected 'Syllable breakdown:' in feedback."

    # Print for debug
    print("Score:", score)
    for fmsg in feedback:
        print("-", fmsg)
