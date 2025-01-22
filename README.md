
# For haiku, the registry says there's one argument: --tolerance
uv run cli.py samples/poetry/haikus/my_haiku.txt --verifier=haiku --feedback
uv run cli.py samples/my_haiku_invalid.txt --verifier=haiku --feedback

# For limerick, the registry says arguments: --line_count_required, --long_min, ...
uv run cli.py samples/poetry/limericks/my_limerick.txt --verifier=limerick --feedback
uv run cli.py samples/poetry/limericks/my_limerick_invalid.txt --verifier=limerick --feedback
