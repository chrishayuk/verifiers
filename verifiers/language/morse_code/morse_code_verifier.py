import sys
from verifiers.base_verifier import BaseVerifier

def text_to_morse(text: str) -> str:
    """
    Convert a given text string into its Morse code representation.
    """
    morse_dict = {
        'A': '.-',    'B': '-...',  'C': '-.-.',  'D': '-..',
        'E': '.',     'F': '..-.',  'G': '--.',   'H': '....',
        'I': '..',    'J': '.---',  'K': '-.-',   'L': '.-..',
        'M': '--',    'N': '-.',    'O': '---',   'P': '.--.',
        'Q': '--.-',  'R': '.-.',   'S': '...',   'T': '-',
        'U': '..-',   'V': '...-',  'W': '.--',   'X': '-..-',
        'Y': '-.--',  'Z': '--..',
        '0': '-----', '1': '.----', '2': '..---', '3': '...--',
        '4': '....-', '5': '.....', '6': '-....', '7': '--...',
        '8': '---..', '9': '----.',
        ',': '--..--', '.': '.-.-.-', '?': '..--..', ';': '-.-.-.',
        ':': '---...', "'": '.----.', '-': '-....-', '/': '-..-.',
        '(': '-.--.',  ')': '-.--.-', '"': '.-..-.'
    }

    text = text.upper()
    morse_code_parts = []

    for char in text:
        if char in morse_dict:
            morse_code_parts.append(morse_dict[char])
        elif char.isspace():
            # Use a slash to represent space between words
            morse_code_parts.append('/')
        else:
            # For characters not in the dictionary, mark them with '?'
            morse_code_parts.append('?')

    return ' '.join(morse_code_parts)


def morse_to_text(morse: str) -> str:
    """
    Decode a Morse code string back to plain English.
    We'll:
      - Split on spaces to get tokens (each token is a letter code or '/')
      - Map each token back to its corresponding character
      - We'll treat '/' as space, or if unknown token, mark with '?'
    """
    # Invert the text_to_morse dictionary to map '.-' => 'A', etc.
    inverse_morse_dict = {
        '.-': 'A',   '-...': 'B', '-.-.': 'C',  '-..': 'D',
        '.': 'E',    '..-.': 'F', '--.': 'G',   '....': 'H',
        '..': 'I',   '.---': 'J', '-.-': 'K',   '.-..': 'L',
        '--': 'M',   '-.': 'N',   '---': 'O',   '.--.': 'P',
        '--.-': 'Q', '.-.': 'R',  '...': 'S',   '-': 'T',
        '..-': 'U',  '...-': 'V', '.--': 'W',   '-..-': 'X',
        '-.--': 'Y', '--..': 'Z',
        '-----': '0','.----': '1','..---': '2','...--': '3',
        '....-': '4','.....': '5','-....': '6','--...': '7',
        '---..': '8','----.': '9',
        '--..--': ',', '.-.-.-': '.', '..--..': '?', '-.-.-.': ';',
        '---...': ':', '.----.': "'", '-....-': '-', '-..-.': '/',
        '-.--.': '(', '-.--.-': ')', '.-..-.': '"'
    }

    tokens = morse.split()
    decoded_chars = []

    for tok in tokens:
        if tok == '/':
            decoded_chars.append(' ')  # space
        elif tok in inverse_morse_dict:
            decoded_chars.append(inverse_morse_dict[tok])
        else:
            decoded_chars.append('?')  # unknown token

    # Join up all decoded characters (including spaces).
    return ''.join(decoded_chars)


class MorseCodeVerifier(BaseVerifier):
    def __init__(self):
        """
        Parameters:
          - original_text: the reference text (in plain English if verify_mode='encode',
                           or in Morse code if verify_mode='decode').
          - verify_mode: "encode" => we expect the candidate text to be Morse,
                         "decode" => we expect the candidate text to be plain English.
        """
        super().__init__(
            name="morse_code_verifier",
            description="Verifies correctness of Morse code in both encoding and decoding directions.",
            parameters={
                "original_text": {
                    "type": "string",
                    "description": "The reference text: plain English (encode mode) or Morse code (decode mode)."
                },
                "verify_mode": {
                    "type": "string",
                    "default": "encode",
                    "description": "Either 'encode' (candidate is Morse) or 'decode' (candidate is plain text)."
                }
            }
        )

    def verify(self, text: str,
               original_text: str = "",
               verify_mode: str = "encode",
               **kwargs) -> float:
        """
        Simple wrapper returning a score in [0,1].
        """
        result = self.verify_with_feedback(
            text=text,
            original_text=original_text,
            verify_mode=verify_mode,
            **kwargs
        )
        return result["score"]

    def verify_with_feedback(self, text: str,
                             original_text: str = "",
                             verify_mode: str = "encode",
                             **kwargs) -> dict:
        """
        Returns a dict:
          {
            "score": float in [0,1],
            "feedback": list of diagnostic messages
          }

        - "encode" mode:
            * original_text -> plain English
            * text -> candidate Morse
            * Compare to text_to_morse(original_text).
            * Token-by-token match for partial credit.

        - "decode" mode:
            * original_text -> Morse
            * text -> candidate plain English
            * Compare text to morse_to_text(original_text) char-by-char for partial credit.
        """
        feedback = []
        score = 0.0

        if verify_mode not in ["encode", "decode"]:
            feedback.append(f"Invalid verify_mode: '{verify_mode}'. Expected 'encode' or 'decode'.")
            return {"score": 0.0, "feedback": feedback}

        # ------------------------- ENCODE MODE -------------------------
        if verify_mode == "encode":
            reference_morse = text_to_morse(original_text)
            ref_tokens = reference_morse.split()
            cand_tokens = text.split()

            if not ref_tokens or not cand_tokens:
                feedback.append("Either reference or candidate tokens are empty.")
                return {"score": 0.0, "feedback": feedback}

            matches = 0
            max_len = max(len(ref_tokens), len(cand_tokens))
            compare_len = min(len(ref_tokens), len(cand_tokens))

            for i in range(compare_len):
                if ref_tokens[i] == cand_tokens[i]:
                    matches += 1
                else:
                    feedback.append(
                        f"Token mismatch at index {i}: "
                        f"expected '{ref_tokens[i]}', got '{cand_tokens[i]}'"
                    )

            if len(ref_tokens) != len(cand_tokens):
                feedback.append(
                    f"Token count mismatch: reference has {len(ref_tokens)}, "
                    f"candidate has {len(cand_tokens)}."
                )

            score = matches / max_len if max_len else 0.0
            feedback.append(f"(Encode) Reference Morse: '{reference_morse}'")
            feedback.append(f"(Encode) Candidate Morse: '{text}'")
            feedback.append(f"(Encode) Match count = {matches} / {max_len}")
            feedback.append(f"(Encode) Score = {score:.2f}")

        # ------------------------- DECODE MODE -------------------------
        else:
            decoded_text = morse_to_text(original_text)
            ref_chars = list(decoded_text.upper())
            cand_chars = list(text.upper())

            if not ref_chars or not cand_chars:
                feedback.append("Either reference or candidate text is empty.")
                return {"score": 0.0, "feedback": feedback}

            matches = 0
            max_len = max(len(ref_chars), len(cand_chars))
            compare_len = min(len(ref_chars), len(cand_chars))

            for i in range(compare_len):
                if ref_chars[i] == cand_chars[i]:
                    matches += 1
                else:
                    feedback.append(
                        f"Character mismatch at index {i}: "
                        f"expected '{ref_chars[i]}', got '{cand_chars[i]}'"
                    )

            if len(ref_chars) != len(cand_chars):
                feedback.append(
                    f"Character count mismatch: reference has {len(ref_chars)}, "
                    f"candidate has {len(cand_chars)}."
                )

            score = matches / max_len if max_len else 0.0
            feedback.append(f"(Decode) Original Morse: '{original_text}'")
            feedback.append(f"(Decode) Decoded as: '{decoded_text}'")
            feedback.append(f"(Decode) Candidate text: '{text}'")
            feedback.append(f"(Decode) Match count = {matches} / {max_len}")
            feedback.append(f"(Decode) Score = {score:.2f}")

        return {"score": score, "feedback": feedback}
