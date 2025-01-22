import pytest
from verifiers.poetry.villanelle_verifier import VillanelleVerifier

@pytest.fixture
def verifier():
    return VillanelleVerifier()

def test_not_nineteen_lines(verifier):
    """
    If a poem doesn't have 19 lines, we expect a partial or zero score. 
    By default, your code returns line_count_weight * (num_lines==19 ? 1 : 0).
    Because it's not 19, line_count_score=0 => final=0.0
    """
    text = """\
Line one
Line two
Line three
"""
    score = verifier.verify(text)
    assert score == 0.0, f"Expected 0.0, got {score}"

def test_bad_repetitions(verifier):
    """
    If the poem has 19 lines but doesn't repeat lines 1 and 3 
    properly at 6,9,12,15,18,19, we see partial penalty 
    (some fraction <1.0 if line_count is correct but others fail).
    """
    poem = "\n".join(f"Line {i+1}" for i in range(19))
    # This definitely won't meet the repetition requirement or the rhyme scheme.
    score = verifier.verify(poem)
    assert 0.0 <= score < 1.0, f"Expected partial, got {score}"

def test_perfect_villanelle_example(verifier):
    """
    Insert an example that meets all criteria:
     - 19 lines
     - Proper refrain repetition (lines 6,12,18 = line1; lines 9,15,19 = line3)
     - A/B rhyme scheme with line1 & line2 as reference
    This is a contrived example for testing only.
    """
    poem_lines = [
        "I have a cat",          # (1) repeated at 6,12,18
        "We love our dog",       # (2)
        "Another cat",           # (3) repeated at 9,15,19
        "random cat",            # (4) (A)
        "random dog",            # (5) (B)
        "I have a cat",          # (6) repeat line1
        "random cat",            # (7) (A)
        "random dog",            # (8) (B)
        "Another cat",           # (9) repeat line3
        "random cat",            # (10) (A)
        "random dog",            # (11) (B)
        "I have a cat",          # (12) repeat line1
        "random cat",            # (13) (A)
        "random dog",            # (14) (B)
        "Another cat",           # (15) repeat line3
        "random cat",            # (16) (A)
        "random dog",            # (17) (B)
        "I have a cat",          # (18) repeat line1
        "Another cat"            # (19) repeat line3
    ]
    poem = "\n".join(poem_lines)
    score = verifier.verify(poem)
    # We expect a full score of 1.0 if everything is perfect.
    assert score == 1.0, f"Expected 1.0, got {score}"

# --- New test for feedback with partial scenario --- #
def test_villanelle_feedback(verifier):
    """
    Test .verify_with_feedback for partial results and feedback messages.
    Let's make a poem with 10 lines only, so line_count_fraction=10/19=0.526..., 
    zero repetition matches, zero A/B rhyme lines if lines>2, etc.
    We'll see a partial final score >0 if it can match some minimal rhyme or 0 if not.
    """
    poem = """\
Line 1
Line 2
Line 3
Line 4
Line 5
Line 6
Line 7
Line 8
Line 9
Line 10
"""
    result = verifier.verify_with_feedback(poem)
    score = result["score"]
    feedback = result["feedback"]

    assert 0.0 <= score <= 1.0, "Score out of range"
    assert isinstance(feedback, list), "Feedback should be a list of strings"

    print("\nVillanelle Feedback Test:")
    print("Score:", score)
    print("Feedback:")
    for msg in feedback:
        print(" -", msg)

    # We expect partial line count (10/19 => ~0.526 if line_count_weight=0.2 => 0.1052),
    # repetition fraction = 0 (not enough lines to meet repeats), 
    # rhyme fraction might be 0 if lines aren't rhyming 
    # => final partial or near 0. 
    # We'll just confirm it's less than 1.0
    assert score < 1.0, f"Expected partial (<1.0), got {score}"
