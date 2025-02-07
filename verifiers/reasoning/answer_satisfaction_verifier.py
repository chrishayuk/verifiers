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

    Additional nuance:
      - Penalizes slightly if the user's answer does NOT restate the question in some form.
    """

    ANSWER_PATTERN = re.compile(r"<answer>(.*?)</answer>", re.DOTALL | re.IGNORECASE)

    def __init__(self, name="satisfaction_verifier", default_model="llama3.1"):
        super().__init__(
            name=name,
            description=(
                "Scores an <answer> for correctness, clarity, style, completeness, "
                "and partial repetition of the question, using Ollama structured outputs."
            ),
            parameters={}
        )
        self.logger = logging.getLogger(name)
        self.default_model = default_model

    def verify(self, text: str, **kwargs) -> float:
        """Returns only the numeric score."""
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
            feedback.append("No <answer>...</answer> found => score=0.0.")
            return {"score": 0.0, "feedback": feedback}

        answer = answer_match.group(1).strip()
        if not answer:
            feedback.append("No <answer>...</answer> found => score=0.0.")
            return {"score": 0.0, "feedback": feedback}

        # 2) Build the system prompt
        #    Include instructions to penalize if the question isn't referenced at all.
        prompt = f"""
You are an AI scoring engine. Return valid JSON:

{{
  "score": <float in [0.0, 1.0]>,
  "feedback": "<short explanation>"
}}

### SCORING CRITERIA
1. If the answer is correct, start from 1.0.
2. Deduct up to 0.1 if clarity, grammar, or style are significantly lacking.
3. Deduct up to 0.1 if the answer doesn't reference the key part of the question (like the numbers or statement).
4. Never reduce the score below 0.0.

### USER’S ANSWER
{answer}

### INSTRUCTIONS
- Provide a final JSON with "score" and "feedback".
- Example:
{{
  "score": 1.0,
  "feedback": "Perfectly addresses the question and is written clearly."
}}
"""

        try:
            # 3) Call Ollama with the structured output format
            response = chat(
                model=self.default_model,
                messages=[{"role": "system", "content": prompt}],
                format=AnswerEvaluation.model_json_schema(),
            )
            llm_output = response.message.content.strip()
            self.logger.debug(f"Raw LLM output: {llm_output}")

            # 4) Parse JSON into our Pydantic model
            evaluation = AnswerEvaluation.model_validate_json(llm_output)

            # 5) Clamp score
            clamped_score = max(0.0, min(evaluation.score, 1.0))

            if evaluation.feedback:
                feedback.append(f"LLM feedback: {evaluation.feedback}")

            return {"score": clamped_score, "feedback": feedback}

        except Exception as e:
            msg = f"Error calling LLM or parsing JSON => {e} => score=0.0."
            feedback.append(msg)
            self.logger.error(msg)
            return {"score": 0.0, "feedback": feedback}
