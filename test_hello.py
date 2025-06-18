import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / 'hello.py'

def test_default_greeting():
    result = subprocess.run([
        sys.executable,
        str(SCRIPT),
    ], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == 'Hello, world'


def test_custom_name():
    result = subprocess.run([
        sys.executable,
        str(SCRIPT),
        '--name', 'Alice',
    ], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == 'Hello, Alice'
