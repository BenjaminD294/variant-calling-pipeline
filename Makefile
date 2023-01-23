install:
	@poetry install

package:
	@zip -r vcp.zip * .[^.]* -x .git/\* .venv/\* vendor/\* temp/\* out/\* src/**/__pycache__/\*

run:
	@poetry run python src/main.py
