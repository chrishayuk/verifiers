```bash
uv run fastapi_server.py
```

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "verifier": "morse_code",
    "feedback": true,
    "args": {
      "original_text": "HELLO WORLD",
      "verify_mode": "encode"
    },
    "text": ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."
  }'
```

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
        "verifier": "morse_code",
        "feedback": true,
        "args": {
          "original_text": ".... . .-.. .-.. --- / .-- --- .-. .-.. -..",
          "verify_mode": "decode"
        },
        "text": "HELLO WORLD"
      }'
```


```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
        "text": "There once was a fellow named Lee\nHe was stung on the arm by a bee\nHe jumped with a start\nThen soon had a fart\nAnd happily ended up free",
        "verifier": "limerick",
        "feedback": true
      }'
```

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
        "text": "<think>The sum of 3 and 4 is calculated by adding the two numbers together. 3 + 4 equals 7.</think><answer>7</answer>",
        "verifier": "reasoning_format",
        "feedback": true
      }'
```

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "\\(\\boxed{4}\\)",
    "verifier": "boxed_answer",
    "feedback": true,
    "args": {
      "gold_solution": "\\(\\boxed{4}\\)"
    }
  }'
```

```bash
curl -X POST http://localhost:8000/verify \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Here is my final solution: <verifier_answer>4</verifier_answer>",
    "verifier": "verifier_answer",
    "feedback": true,
    "args": {
      "gold_solution": "4"
    }
  }'
```

# math
uv run cli.py samples/math/valid_boxed_answer.txt --verifier=boxed_answer --feedback --gold_solution="\(\boxed{4}\)"
uv run cli.py samples/math/invalid_boxed_answer.txt --verifier=boxed_answer --feedback --gold_solution="\(\boxed{4}\)"

uv run cli.py samples/reasoning/verifier_answer/valid_verifier_answer.txt \
  --verifier=verifier_answer \
  --feedback \
  --gold_solution="4"

uv run cli.py samples/reasoning/verifier_answer/invalid_verifier_answer.txt \
  --verifier=verifier_answer \
  --feedback \
  --gold_solution="4"


# reasoning
uv run cli.py samples/reasoning/reasoning_format/valid_reasoning_format.txt --verifier=reasoning_format --feedback
uv run cli.py samples/reasoning/reasoning_format/invalid_reasoning_format.txt --verifier=reasoning_format --feedback

# haiku
uv run cli.py samples/poetry/haikus/valid_haiku.txt --verifier=haiku --feedback
uv run cli.py samples/poetry/haikus/invalid_haiku.txt --verifier=haiku --feedback
uv run cli.py samples/poetry/haikus/granite_haiku.txt --verifier=haiku --feedback
uv run cli.py samples/poetry/haikus/phi4_haiku_.txt --verifier=haiku --feedback

# limerick
uv run cli.py samples/poetry/limericks/valid_limerick.txt --verifier=limerick --feedback
uv run cli.py samples/poetry/limericks/invalid_limerick.txt --verifier=limerick --feedback

# rhyme
uv run cli.py samples/poetry/rhymes/valid_rhyme.txt --verifier=rhyme --feedback
uv run cli.py samples/poetry/rhymes/invalid_rhyme.txt --verifier=rhyme --feedback

# tanka
uv run cli.py samples/poetry/tankas/good_tanka.txt --verifier=tanka --feedback
uv run cli.py samples/poetry/tankas/invalid_tanka.txt --verifier=tanka --feedback



Your poem scored {score:0.50}, below the threshold of 1.
The verifier’s feedback was:
 - Line count check passed (5 lines).
 - A-rhyme check failed (lines 1,2,5).
 - B-rhyme check passed (lines 3,4).
 - Lines 1,2,5 syllable check failed: (Line1=7, Line2=10, Line5=12) Expected 7-11.
  ...

Please revise your poem to address these issues, but keep the style/theme.

Your poem scored {score:1.00}, meeting the threshold of 1.
The verifier’s feedback was:
 - Line count check passed (5 lines).
 - A-rhyme check passed (lines 1,2,5).
 - B-rhyme check passed (lines 3,4).
 - Syllable count check passed.
 

 Score: 1.00
Feedback:
 - Line count check passed (5 lines).
 - A-rhyme check passed (lines 1,2,5).
 - B-rhyme check passed (lines 3,4).
 - Syllable count check passed.


Your limerick scored {score:0.75}, below the threshold of 1.
The verifier’s feedback was:
 - Line count check passed (5 lines).
 - A-rhyme check failed (lines 1,2,5).
 - B-rhyme check passed (lines 3,4).
 - Syllable count check passed.
   ...

Please revise your limerick to address these issues, but keep the style/theme.

Your limerick scored {score:0.50}, below the threshold of 1.
The verifier’s feedback was:
 - Line count check passed (5 lines).
 - A-rhyme check failed (lines 1,2,5).
 - B-rhyme check failed (lines 3,4).
 - Syllable count check passed.
   ...

Please revise your limerick to address these issues, but keep the style/theme.


Your limerick scored {score:0.75}, below the threshold of 1.
The verifier’s feedback was:
 - Line count check passed (5 lines).
 - A-rhyme check passed (lines 1,2,5).
 - B-rhyme check passed (lines 3,4).
 - Lines 1,2,5 syllable check failed: (Line1=10, Line2=12, Line5=10) Expected 7-11.
   ...

Please revise your limerick to address these issues, but keep the style/theme.

Your limerick scored {score:0.75}, below the threshold of 1.
The verifier’s feedback was:
Feedback:
 - Line count check passed (5 lines).
 - A-rhyme check passed (lines 1,2,5).
 - B-rhyme check passed (lines 3,4).
 - Lines 1,2,5 syllable check failed: (Line1=9, Line2=12, Line5=10) Expected 7-11.
    ...

Please revise your limerick to address these issues, but keep the style/theme.



