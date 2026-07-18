"""
Minimal smoke tests for the parser and sanity systems.

Run directly with: python tests/test_engine.py
(No pytest dependency required yet - kept stdlib-only for now.)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from game.parser import parse
from game.sanity import SanityTier, distort, tier_for


def test_parser_basic_verbs():
    assert parse("look").verb == "look"
    assert parse("l").verb == "look"
    assert parse("").verb == "empty"
    assert parse("asdkjhaskjd").verb == "unknown"


def test_parser_movement():
    cmd = parse("go north")
    assert cmd.verb == "go" and cmd.direction == "north"

    cmd = parse("n")
    assert cmd.verb == "go" and cmd.direction == "north"


def test_parser_target():
    cmd = parse("take brass key")
    assert cmd.verb == "take"
    assert cmd.target == "brass key"


def test_sanity_tiers():
    assert tier_for(100) == SanityTier.LUCID
    assert tier_for(80) == SanityTier.LUCID
    assert tier_for(79) == SanityTier.UNEASY
    assert tier_for(50) == SanityTier.UNEASY
    assert tier_for(49) == SanityTier.FRAYING
    assert tier_for(25) == SanityTier.FRAYING
    assert tier_for(24) == SanityTier.BROKEN
    assert tier_for(0) == SanityTier.BROKEN


def test_distort_lucid_unchanged():
    text = "The room is quiet."
    assert distort(text, 100) == text


def run_all():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for t in tests:
        t()
        print(f"  ok  {t.__name__}")
    print(f"\n{len(tests)} tests passed.")


if __name__ == "__main__":
    run_all()
