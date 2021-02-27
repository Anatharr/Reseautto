
# Create virtual environment in .venv folder
python -m venv .venv

# Activate the venv
.\.venv\Scripts\Activate.ps1

# Install all required packages for the project
pip install -r requirements.txt

# Set-up pre-commit hooks
if ("--production" -eq $args[0]) {
	echo "Finished production building"
}
else {
	echo "Pre-commit installation..."
	pre-commit install
}