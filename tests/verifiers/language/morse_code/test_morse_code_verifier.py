# test_morse_code_verifier.py
import pytest

# imports
from verifiers.language.morse_code.morse_code_verifier import MorseCodeVerifier


@pytest.fixture
def verifier():
    """Pytest fixture to create a fresh instance of MorseCodeVerifier for each test."""
    return MorseCodeVerifier()


def test_encode_exact_match(verifier):
    """
    Test that encode mode returns a perfect score (1.0) when the candidate Morse
    exactly matches the reference Morse of the given text.
    """
    original_text = "HELLO"
    # Morse for "HELLO": ".... . .-.. .-.. ---"
    candidate_morse = ".... . .-.. .-.. ---"
    
    result = verifier.verify_with_feedback(
        text=candidate_morse,
        original_text=original_text,
        verify_mode="encode"
    )
    assert result["score"] == 1.0, "Score should be 1.0 for exact match."
    assert not any("mismatch" in line.lower() for line in result["feedback"]), \
        "Feedback should not report any mismatches for an exact match."


def test_encode_partial_match(verifier):
    """
    Test encode mode returns a partial score if there's a token mismatch.
    For instance, "HELLO" => 5 tokens. If 1 token is wrong, expect 4/5 = 0.8 score.
    """
    original_text = "HELLO"
    # Correct: ".... . .-.. .-.. ---"
    # We'll introduce a mismatch in the 3rd token:
    candidate_morse = ".... . .-... .-.. ---"  # 3rd token .-... is incorrect
    
    result = verifier.verify_with_feedback(
        text=candidate_morse,
        original_text=original_text,
        verify_mode="encode"
    )
    # Score = 4 matches out of 5 tokens = 0.8
    assert pytest.approx(result["score"], 0.01) == 0.8, \
        f"Expected a partial score of 0.8, got {result['score']}"
    assert any("mismatch" in line.lower() for line in result["feedback"]), \
        "Feedback should indicate a token mismatch."


def test_encode_length_mismatch(verifier):
    """
    Test encode mode if candidate Morse has different number of tokens than the reference.
    """
    original_text = "SOS"
    # Morse for "SOS": "... --- ..."
    # We'll add an extra token at the end
    candidate_morse = "... --- ... ...."
    
    result = verifier.verify_with_feedback(
        text=candidate_morse,
        original_text=original_text,
        verify_mode="encode"
    )
    # The reference has 3 tokens; candidate has 4 => max_len = 4
    # If the first 3 match exactly, we get 3 matches out of 4 => 0.75
    assert pytest.approx(result["score"], 0.01) == 0.75, \
        f"Expected score of 0.75, got {result['score']}"
    assert any("token count mismatch" in line.lower() for line in result["feedback"]), \
        "Feedback should mention token count mismatch."


def test_decode_exact_match(verifier):
    """
    Test decode mode returns a perfect score for an exact character match.
    We'll decode Morse ".... . .-.. .-.. ---" => "HELLO".
    """
    original_morse = ".... . .-.. .-.. ---"
    candidate_text = "HELLO"
    
    result = verifier.verify_with_feedback(
        text=candidate_text,
        original_text=original_morse,
        verify_mode="decode"
    )
    assert result["score"] == 1.0, "Score should be 1.0 for exact decode match."
    assert not any("mismatch" in line.lower() for line in result["feedback"]), \
        "Feedback should not report mismatches if it's an exact match."


def test_decode_partial_match(verifier):
    """
    Test decode mode returns partial credit when characters differ.
    For "HELLO" => ".... . .-.. .-.. ---", if candidate has 1 char wrong => partial.
    """
    original_morse = ".... . .-.. .-.. ---"  # Decodes to "HELLO"
    candidate_text = "HELLU"  # Last character is different

    result = verifier.verify_with_feedback(
        text=candidate_text,
        original_text=original_morse,
        verify_mode="decode"
    )
    # "HELLO" vs "HELLU" => 4 matches, 1 mismatch => total length 5 => 4/5 = 0.8
    assert pytest.approx(result["score"], 0.01) == 0.8, \
        f"Expected partial score of 0.8, got {result['score']}"
    assert any("character mismatch" in line.lower() for line in result["feedback"]), \
        "Feedback should report the character mismatch."


def test_decode_length_mismatch(verifier):
    """
    Test decode mode if the candidate text is longer/shorter than the decoded reference.
    """
    original_morse = "... --- ..."
    # This decodes to "SOS" => length 3. If candidate has 4 chars, partial = 3/4 = 0.75
    candidate_text = "SOST"  # extra char

    result = verifier.verify_with_feedback(
        text=candidate_text,
        original_text=original_morse,
        verify_mode="decode"
    )
    assert pytest.approx(result["score"], 0.01) == 0.75, \
        f"Expected 0.75 score, got {result['score']}"
    assert any("character count mismatch" in line.lower() for line in result["feedback"]), \
        "Feedback should mention character count mismatch."
