hello:
	echo "Welcome to spotify-proj."

install-dependencies:
	echo "Installing dependencies..."
	poetry install
	echo "DONE"

format:
	echo "Formatting code..."
	black src/