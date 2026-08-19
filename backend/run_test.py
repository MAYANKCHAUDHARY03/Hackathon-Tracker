import pytest
import sys

if __name__ == "__main__":
    sys.exit(pytest.main(["tests/test_portable_project.py", "-v", "--tb=native"]))
