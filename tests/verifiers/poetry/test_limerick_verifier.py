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
    # If line count fails, it might still pass the other checks for partial credit,
    # so let's just confirm it's below 1.0. Could be 0.75, 0.5, etc.
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
    # lines[0], lines[1] fail => no perfect A-rhyme => not 1.0
    score = verifier.verify(text)
    # Could be 0.75 if line_count, B-rhyme, syllables are okay
    # or 0.5 if something else fails, etc. Just confirm <1.0
    assert 0.0 <= score < 1.0, f"Expected partial (<1.0), got {score}"

def test_syllable_count_failure(verifier):
    """
    If lines 1,2,5 or 3,4 don't meet syllable ranges,
    we fail that check but can still pass other checks => partial.
    """
    text = """\
Meow
Who was stung on the arm by a bee
When asked, "Does it hurt?"
"No, it doesn't," he spurt
It’s a good thing it wasn’t a flea.
"""
    # line 1 definitely won't meet the 7-11 range => lose that point, 
    # but might pass line_count, A-rhyme, B-rhyme => partial
    score = verifier.verify(text)
    assert 0.0 <= score < 1.0, f"Expected partial, got {score}"

def test_custom_parameters(verifier):
    """
    Overriding defaults, e.g. line_count_required=3, might pass line-count 
    but fail others => partial. 
    Old code expected 0.0; now we just confirm <1.0 if not all are correct.
    """
    text = """\
Not exactly five lines
But let's see if the param
Helps or not
"""
    # By default, line_count_required=5 => not perfect => <1.0
    score_default = verifier.verify(text)
    assert 0.0 <= score_default < 1.0, f"Expected <1.0, got {score_default}"
    
    # Now force 3 lines => line count passes => might pass 1 check,
    # but likely fails rhyme or syllable => partial <1.0
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
    # Suppose lines 1,2,5 might rhyme, lines 3,4 might or might not => partial
    result = verifier.verify_with_feedback(text)
    score = result["score"]
    feedback = result["feedback"]

    assert 0.0 <= score <= 1.0, f"Score {score} out of range"
    assert isinstance(feedback, list), "Feedback should be a list"
    assert len(feedback) > 0, "Expected feedback messages"

    print("Score:", score)
    for msg in feedback:
        print("-", msg)

    # Optionally check that certain lines mention "A-rhyme" pass/fail, 
    # "B-rhyme" pass/fail, etc.
