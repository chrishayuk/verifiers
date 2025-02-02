import pytest
from verifiers.reasoning.reasoning_format_verifier import ReasoningFormatVerifier

@pytest.fixture
def verifier():
    return ReasoningFormatVerifier()

def test_valid_reasoning_format(verifier):
    text = """<think>
    The sum of 3 and 4 is calculated by adding the two numbers together. 
    3 + 4 equals 7.
    </think>
    <answer>7</answer>"""
    
    result = verifier.verify_with_feedback(text)
    assert result["score"] == 1.0
    assert "✅ Text correctly includes both <think> and <answer> tags with valid content." in result["feedback"]

def test_missing_answer_tag(verifier):
    text = """<think>
    The sum of 3 and 4 is calculated by adding the two numbers together.
    </think>"""
    
    result = verifier.verify_with_feedback(text)
    assert result["score"] == 0.0
    assert any("Text does not conform to the required format." in msg for msg in result["feedback"])
    assert any("Ensure it follows: <think>reasoning...</think><answer>final answer...</answer>." in msg for msg in result["feedback"])

def test_empty_think_section(verifier):
    text = """<think></think>
    <answer>7</answer>"""
    
    result = verifier.verify_with_feedback(text)
    assert result["score"] == 0.0
    assert any("The <think> section is empty. It must contain reasoning steps." in msg for msg in result["feedback"])

def test_empty_answer_section(verifier):
    text = """<think>
    The sum of 3 and 4 is calculated by adding the two numbers together.
    </think>
    <answer></answer>"""
    
    result = verifier.verify_with_feedback(text)
    assert result["score"] == 0.0
    assert any("The <answer> section is empty. It must contain a final answer." in msg for msg in result["feedback"])

def test_incorrect_tag_order(verifier):
    text = """<answer>7</answer>
    <think>
    The sum of 3 and 4 is calculated by adding the two numbers together.
    </think>"""
    
    result = verifier.verify_with_feedback(text)
    assert result["score"] == 0.0
    assert any("Text does not conform to the required format." in msg for msg in result["feedback"])
    assert any("Ensure it follows: <think>reasoning...</think><answer>final answer...</answer>." in msg for msg in result["feedback"])

def test_extra_text_outside_tags(verifier):
    text = """Extra text here
    <think>The sum of 3 and 4 is 7.</think>
    <answer>7</answer>"""
    
    result = verifier.verify_with_feedback(text)
    assert result["score"] == 0.0
    assert any("Text does not conform to the required format." in msg for msg in result["feedback"])
    assert any("Ensure it follows: <think>reasoning...</think><answer>final answer...</answer>." in msg for msg in result["feedback"])

def test_whitespace_tolerance(verifier):
    text = """  <think>
    The sum of 3 and 4 is 7.
    </think>
    
    <answer>7</answer>  """
    
    result = verifier.verify_with_feedback(text)
    assert result["score"] == 1.0
    assert "✅ Text correctly includes both <think> and <answer> tags with valid content." in result["feedback"]

def test_multiline_reasoning(verifier):
    text = """<think>
    First, we take the number 3.
    Then, we add 4 to it.
    This results in 7.
    </think>
    <answer>7</answer>"""
    
    result = verifier.verify_with_feedback(text)
    assert result["score"] == 1.0
    assert "✅ Text correctly includes both <think> and <answer> tags with valid content." in result["feedback"]
