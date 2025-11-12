"""Pytest configuration and fixtures for integration tests."""

import sys
from pathlib import Path

# Add backend to Python path
BACKEND_PATH = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_PATH))
