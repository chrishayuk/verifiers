import pytest
from verifiers.poetry.limerick_verifier import LimerickVerifier

@pytest.fixture
def verifier():
    """Returns an instance of LimerickVerifier."""
    return LimerickVerifier()

def test_perfect_limerick(verifier):
    """Test a correct limerick returns a score of 1.0."""
    text = """\
There once was a fellow named Lee
Who was stung on the arm by a bee
   When asked, "Does it hurt?"
   "No, it doesn't," he spurt
It’s a good thing it wasn’t a flea.
"""
    score = verifier.verify(text)
    assert score == 1.0, f"Expected 1.0, got {score}"

def test_incorrect_line_count(verifier):
    """
    Test a poem with fewer (or more) than 5 lines.
    Previously we expected 0.0 strictly, 
    but now we only know it's 'not perfect' => score < 1.0.
    """
    text = """\
There once was a fellow named Lee
Who was stung on the arm by a bee
   When asked, "Does it hurt?"
   "No, it doesn't," he spurt
"""
    score = verifier.verify(text)
    # If line count fails, it might still pass other checks => partial credit, so <1.0
    assert 0.0 <= score < 1.0, f"Expected <1.0, got {score}"

def test_rhyme_failure(verifier):
    """
    If lines 1,2,5 or lines 3,4 don't rhyme properly,
    we lose that check. The poem might still pass others => partial.
    """
    text = """\
There once was a fellow named Lee
Who once had a grand jubilee
   When asked, "Was it fun?"
   "No, it wasn't," he spurt
It’s a good thing it wasn’t a flea.
"""
    # lines[0], lines[1] don't properly rhyme => not 1.0
    score = verifier.verify(text)
    # Could be 0.75 if line_count, B-rhyme, syllables pass
    # or 0.5 if something else fails, etc. Just confirm <1.0
    assert 0.0 <= score < 1.0, f"Expected partial (<1.0), got {score}"

def test_syllable_count_failure(verifier):
    """
    If lines 1,2,5 or 3,4 don't meet syllable ranges,
    that check fails but others might pass => partial.
    """
    text = """\
Meow
Who was stung on the arm by a bee
When asked, "Does it hurt?"
"No, it doesn't," he spurt
It’s a good thing it wasn’t a flea.
"""
    # line 1 definitely won't meet the 7-11 range => lose that point
    score = verifier.verify(text)
    assert 0.0 <= score < 1.0, f"Expected partial, got {score}"

def test_custom_parameters(verifier):
    """
    Overriding defaults, e.g. line_count_required=3, might pass line-count 
    but fail others => partial. 
    """
    text = """\
Not exactly five lines
But let's see if the param
Helps or not
"""
    # By default, line_count_required=5 => not perfect => <1.0
    score_default = verifier.verify(text)
    assert 0.0 <= score_default < 1.0, f"Expected <1.0, got {score_default}"
    
    # Now force 3 lines => line count passes => might pass that check
    # but fail rhyme or syllable => partial <1.0
    score_custom = verifier.verify(text, line_count_required=3)
    assert 0.0 <= score_custom < 1.0, f"Expected <1.0, got {score_custom}"

def test_feedback(verifier):
    """
    New test that checks feedback. We'll use a partial-limerick
    so we see partial pass/fail messages.
    """
    text = """\
There once was a cat from Peru
Who liked to meow at the zoo
She rarely would nap
She gave a loud clap
Then ended the day feeling blue
"""
    result = verifier.verify_with_feedback(text)
    score = result["score"]
    feedback = result["feedback"]

    assert 0.0 <= score <= 1.0, f"Score {score} out of range"
    assert isinstance(feedback, list), "Feedback should be a list"
    assert len(feedback) > 0, "Expected some feedback messages"

    # Print feedback for debugging
    print("Score:", score)
    for msg in feedback:
        print("-", msg)

    # Check for existence of certain key phrases in the feedback
    # that confirm we have line-by-line breakdown and rhyme details.
    assert any("Line 1 (" in f for f in feedback), (
        "Expected feedback about line 1, with line text in quotes"
    )
    assert any("Words:" in f for f in feedback), (
        "Expected listing of words in at least one line's feedback"
    )
    assert any("Syllables per word:" in f for f in feedback), (
        "Expected 'Syllables per word:' in feedback"
    )
    assert any("Syllable breakdown:" in f for f in feedback), (
        "Expected 'Syllable breakdown:' in feedback"
    )
    # Rhyme breakdown checks:
    assert any("A-rhyme detail" in f for f in feedback), (
        "Expected A-rhyme detail in feedback"
    )
    assert any("B-rhyme detail" in f for f in feedback), (
        "Expected B-rhyme detail in feedback"
    )
