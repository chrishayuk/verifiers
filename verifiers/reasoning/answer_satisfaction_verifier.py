# verifiers/reasoning/answer_satisfaction_verifier.py
import re
import json
import logging
from ollama import chat
from pydantic import BaseModel

from verifiers.base_verifier import BaseVerifier


class AnswerEvaluation(BaseModel):
    score: float
    feedback: str


class AnswerSatisfactionVerifier(BaseVerifier):
    """
    A verifier that:
      1) Extracts <answer>...</answer> from 'text'.
      2) Expects 'question' and 'gold_answer' in kwargs.
      3) Uses Ollama structured outputs to produce:
         {
           "score": <float in [0..1]>,
           "feedback": "<short explanation>"
         }
      4) Returns 0.0 if there's any error or parsing issue.
    """

    ANSWER_PATTERN = re.compile(r"<answer>(.*?)</answer>", re.DOTALL | re.IGNORECASE)

    def __init__(self, name="satisfaction_verifier", default_model="test-model"):
        super().__init__(
            name=name,
            description="Scores an <answer> for correctness, style, etc., using Ollama structured outputs.",
            parameters={}
        )
        self.logger = logging.getLogger(name)
        self.default_model = default_model

    def verify(self, text: str, **kwargs) -> float:
        """
        Returns only the numeric score.
        """
        result = self.verify_with_feedback(text, **kwargs)
        return result["score"]

    def verify_with_feedback(self, text: str, **kwargs) -> dict:
        """
        Returns a dict with {"score": float, "feedback": [str, ...]}.
        Expects 'question' and 'gold_answer' in kwargs.
        """
        feedback = []
        question = kwargs.get("question", "No question provided")
        gold_answer = kwargs.get("gold_answer", "No gold answer provided")

        # 1) Extract the user's <answer>
        answer_match = self.ANSWER_PATTERN.search(text)
        if not answer_match:
            # Matches the test suite's expectation:
            # "No <answer>...</answer>" in feedback for missing tag => score=0.0
            feedback.append("No <answer>...</answer> found => score=0.0.")
            return {"score": 0.0, "feedback": feedback}

        answer = answer_match.group(1).strip()
        if not answer:
            # Matches the test suite's expectation for empty <answer></answer>
            feedback.append("No <answer>...</answer> found => score=0.0.")
            return {"score": 0.0, "feedback": feedback}

        # 2) Build a simple prompt for demonstration.
        prompt = f"""
We want to measure how well the user's answer addresses the question:
 - correctness vs gold answer
 - clarity, style, completeness

Question: {question}
User's Answer: {answer}
Gold Answer: {gold_answer}

Return a JSON object with:
{{
  "score": <float in 0..1>,
  "feedback": "<short explanation>"
}}
"""

        try:
            # 3) Call Ollama, enforcing a schema via Pydantic
            response = chat(
                model=self.default_model,
                messages=[{"role": "system", "content": prompt}],
                format=AnswerEvaluation.model_json_schema(),
            )
            llm_output = response.message.content.strip()
            self.logger.debug(f"Raw LLM output: {llm_output}")

            # 4) Parse into our Pydantic model
            evaluation = AnswerEvaluation.model_validate_json(llm_output)

            # 5) Clamp the score to [0.0, 1.0]
            clamped_score = max(0.0, min(evaluation.score, 1.0))

            if evaluation.feedback:
                feedback.append(f"LLM feedback: {evaluation.feedback}")

            return {"score": clamped_score, "feedback": feedback}

        except Exception as e:
            # Must include "Error calling LLM or parsing JSON" for test_mock_invalid_json_output
            msg = f"Error calling LLM or parsing JSON => {e} => score=0.0."
            feedback.append(msg)
            self.logger.error(msg)
            return {"score": 0.0, "feedback": feedback}
