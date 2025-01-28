
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



