# test_answer_satisfaction_verifier.py
import pytest
import json
from unittest.mock import patch, MagicMock

from verifiers.reasoning.answer_satisfaction_verifier import AnswerSatisfactionVerifier

@pytest.fixture
def verifier():
    """Return an instance of the AnswerSatisfactionVerifier."""
    return AnswerSatisfactionVerifier(default_model="test-model")

def test_no_answer_tag(verifier):
    """
    If the text passed to the verifier has no <answer>...</answer> tag,
    the verifier should return {"score": 0.0, "feedback": [...]}.
    """
    text_without_answer = "Here is some text, but no answer tags."
    result = verifier.verify_with_feedback(text_without_answer, question="What is 2+2?", gold_answer="4")

    assert result["score"] == 0.0
    assert any("No <answer>...</answer>" in msg for msg in result["feedback"])


def test_empty_answer_tag(verifier):
    """
    If the <answer></answer> tag is present but empty, also expect 0.0 score.
    """
    text_empty_answer = "<answer></answer>"
    result = verifier.verify_with_feedback(text_empty_answer, question="What is 2+2?", gold_answer="4")

    assert result["score"] == 0.0
    assert any("No <answer>...</answer>" in msg for msg in result["feedback"])


@patch("verifiers.reasoning.answer_satisfaction_verifier.chat")
def test_mock_valid_json_output(mock_chat, verifier):
    """
    Test a scenario where Ollama returns a valid JSON string that matches the schema.
    """
    # Mock the response from Ollama:
    # Suppose the LLM returns valid JSON with "score" = 0.7, "feedback" = "Decent answer..."
    mock_chat.return_value.message.content = json.dumps({
        "score": 0.7,
        "feedback": "Decent answer with correct style."
    })

    text_with_answer = "<answer>The sum of 2 and 2 is 4.</answer>"
    result = verifier.verify_with_feedback(
        text_with_answer,
        question="What is 2+2?",
        gold_answer="4"
    )

    assert result["score"] == 0.7
    assert any("Decent answer with correct style." in msg for msg in result["feedback"])
    mock_chat.assert_called_once()


@patch("verifiers.reasoning.answer_satisfaction_verifier.chat")
def test_mock_invalid_json_output(mock_chat, verifier):
    """
    Test a scenario where Ollama returns something that is NOT valid JSON,
    e.g. an empty string or partial text, which should lead to score=0.0.
    """
    mock_chat.return_value.message.content = "not valid JSON at all"

    text_with_answer = "<answer>The sum of 2 and 2 is 4.</answer>"
    result = verifier.verify_with_feedback(
        text_with_answer,
        question="What is 2+2?",
        gold_answer="4"
    )

    assert result["score"] == 0.0
    assert any("Error calling LLM or parsing JSON" in msg for msg in result["feedback"])
    mock_chat.assert_called_once()


@patch("verifiers.reasoning.answer_satisfaction_verifier.chat")
def test_score_clamping(mock_chat, verifier):
    """
    Even if Ollama returns a score outside [0.0, 1.0],
    the verifier clamps it to the valid range.
    """
    mock_chat.return_value.message.content = json.dumps({
        "score": 2.5,   # out of range
        "feedback": "Too high but let's see if it's clamped."
    })

    text_with_answer = "<answer>The sum of 2 and 2 is 4.</answer>"
    result = verifier.verify_with_feedback(
        text_with_answer,
        question="What is 2+2?",
        gold_answer="4"
    )

    # The returned score must be clamped to 1.0
    assert result["score"] == 1.0
    assert any("Too high but let's see if it's clamped." in msg for msg in result["feedback"])
    mock_chat.assert_called_once()
