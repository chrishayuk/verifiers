# tests/verifiers/reasoning/test_verifier_answer_verifier.py

import pytest
from verifiers.reasoning.verifier_answer_verifier import VerifierAnswerVerifier

@pytest.fixture
def verifier():
    return VerifierAnswerVerifier()

def test_valid_answer_exact_match(verifier):
    """
    If the final answer is in <verifier_answer>4</verifier_answer>
    and gold_solution="4", we should get score=1.0 with "matches exactly => ..."
    """
    model_output = "<verifier_answer>4</verifier_answer>"
    result = verifier.verify_with_feedback(model_output, gold_solution="4")
    assert result["score"] == 1.0
    assert any("matches exactly" in msg for msg in result["feedback"])

def test_mismatched_answer(verifier):
    """
    If model has <verifier_answer>24</verifier_answer> but gold_solution="4",
    the score should be 0.0 with feedback indicating 'differs => ...'
    """
    model_output = "<verifier_answer>24</verifier_answer>"
    result = verifier.verify_with_feedback(model_output, gold_solution="4")
    assert result["score"] == 0.0
    assert any("differs" in msg for msg in result["feedback"])

def test_no_verifier_tags(verifier):
    """
    If there's no <verifier_answer> tag at all, 
    we expect score=0.0 with a message about missing <verifier_answer>.
    """
    model_output = "No special tags here."
    result = verifier.verify_with_feedback(model_output, gold_solution="42")
    assert result["score"] == 0.0
    assert any("<verifier_answer>" in msg for msg in result["feedback"])

def test_no_gold_solution(verifier):
    """
    If 'gold_solution' is not provided, we skip strict comparison
    and return score=1.0 with feedback saying 'No gold_solution provided'.
    """
    model_output = "<verifier_answer>4</verifier_answer>"
    # Call verify_with_feedback WITHOUT gold_solution
    result = verifier.verify_with_feedback(model_output)
    assert result["score"] == 1.0
    assert any("No gold_solution provided" in msg for msg in result["feedback"])

def test_whitespace_tolerance(verifier):
    """
    If the model answer and gold solution differ only by whitespace,
    .strip() means they match exactly, yielding 1.0.
    """
    model_output = "<verifier_answer>   42   </verifier_answer>"
    result = verifier.verify_with_feedback(model_output, gold_solution="42   ")
    assert result["score"] == 1.0
    assert any("matches exactly" in msg for msg in result["feedback"])
