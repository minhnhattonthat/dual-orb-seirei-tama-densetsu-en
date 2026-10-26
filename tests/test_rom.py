import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))


def test_rom_sha1():
    import check_rom
    try:
        check_rom.check()
    except SystemExit as e:
        if "missing" in str(e):
            pytest.skip(str(e))
        raise
