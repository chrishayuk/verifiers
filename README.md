
# haiku
uv run cli.py samples/poetry/haikus/good_haiku.txt --verifier=haiku --feedback
uv run cli.py samples/poetry/haikusinvalid_haiku_.txt --verifier=haiku --feedback

# limerick
uv run cli.py samples/poetry/limericks/good_limerick.txt --verifier=limerick --feedback
uv run cli.py samples/poetry/limericks/invalid_limerick.txt --verifier=limerick --feedback

# tanka
uv run cli.py samples/poetry/tankas/good_tanka.txt --verifier=tanka --feedback
uv run cli.py samples/poetry/tankas/invalid_tanka.txt --verifier=tanka --feedback

