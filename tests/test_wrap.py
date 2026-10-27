import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import wrap  # noqa: E402


def test_wrap_fits_box_and_keeps_words():
    text = "{hero0}-san, " + " ".join(["adventure"] * 30) + "{fe}Short page.{end}"
    w, bad = wrap.wrap(text)
    assert not bad
    for page in wrap.pages(w):
        assert len(page) <= wrap.LINES
        assert all(wrap.width(line) <= wrap.BOX_PX for line in page)
    assert w.replace("{n}", " ").replace("{fe}", " ").replace("  ", " ") == text.replace("{fe}", " ")


def test_forced_breaks_start_new_page_after_three_lines():
    assert wrap.wrap("a{n}b{n}c{n}d{end}")[0] == "a{n}b{n}c{fe}d{end}"


def test_yes_no_gets_own_line():
    assert wrap.wrap("a{f0}{end}")[0] == "a{n}{f0}{end}"
    assert wrap.wrap("a{n}b{n}c{f0}{end}")[0] == "a{n}b{n}c{fe}{f0}{end}"


def test_overwide_word_reported():
    assert wrap.wrap("W" * 40 + "{end}")[1]
