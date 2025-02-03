# tests/verifiers/math/test_boxed_answer_verifier.py
import pytest
from verifiers.math.boxed_answer_verifier import BoxedAnswerVerifier

@pytest.fixture
def verifier():
    return BoxedAnswerVerifier()

def test_valid_boxed_answer_exact_match(verifier):
    """
    The model's output and gold solution both have the same content in \(\boxed{...}\).
    Should return score=1.0 and success feedback.
    """
    gold_solution = r"\(\boxed{42}\)"
    model_output = r"\(\boxed{42}\)"

    # Pass gold_solution as a kwarg
    result = verifier.verify_with_feedback(text=model_output, gold_solution=gold_solution)
    assert result["score"] == 1.0
    assert any("matches exactly" in msg for msg in result["feedback"])

def test_mismatched_boxed_answer(verifier):
    """
    The model's box content differs from gold.
    Should return score=0.0.
    """
    gold_solution = r"\(\boxed{42}\)"
    model_output = r"\(\boxed{24}\)"  # reversed digits => mismatch

    result = verifier.verify_with_feedback(text=model_output, gold_solution=gold_solution)
    assert result["score"] == 0.0
    assert any("differs" in msg for msg in result["feedback"])

def test_no_box_in_model(verifier):
    """
    Model fails to produce any \(\boxed{...}\) region.
    Expect 0.0 with feedback about no box found.
    """
    gold_solution = r"\(\boxed{7}\)"
    model_output = r"The final answer is 7"

    result = verifier.verify_with_feedback(text=model_output, gold_solution=gold_solution)
    assert result["score"] == 0.0
    assert any("No \\(\\boxed{...}\\)" in msg for msg in result["feedback"])

def test_no_box_in_gold(verifier):
    """
    Gold solution is missing \(\boxed{...}\).
    By default, the verifier returns score=1.0 to avoid penalising the model 
    for unparseable gold data. 
    """
    gold_solution = r"The final answer is 7"  # no box
    model_output = r"\(\boxed{7}\)"

    result = verifier.verify_with_feedback(text=model_output, gold_solution=gold_solution)
    assert result["score"] == 1.0
    assert any("Gold solution has no" in msg for msg in result["feedback"])

def test_extra_spaces_still_exact_match(verifier):
    """
    If both boxes differ by whitespace only around the numeric content,
    the minimal verifier (as implemented) *does* trim content with `.strip()`.
    Hence exact match after trimming passes.
    """
    gold_solution = r"\(\boxed{ 7   }\)"
    model_output = r"\(\boxed{7}\)"

    result = verifier.verify_with_feedback(text=model_output, gold_solution=gold_solution)
    assert result["score"] == 1.0
    assert any("matches exactly" in msg for msg in result["feedback"])

def test_additional_text_outside_box(verifier):
    """
    The model has a correct box, but also extra text outside it. 
    The minimal verifier doesn't penalise extra text. 
    It only looks for the first box match. 
    Confirm it still returns 1.0 if the box matches.
    """
    gold_solution = r"\(\boxed{42}\)"
    model_output = r"Here is the solution: \(\boxed{42}\). Done."

    result = verifier.verify_with_feedback(text=model_output, gold_solution=gold_solution)
    assert result["score"] == 1.0
    assert any("matches exactly" in msg for msg in result["feedback"])
