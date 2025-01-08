import tomllib  # Use `toml` if you're targeting Python <3.11
from pathlib import Path

def get_version():
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]

