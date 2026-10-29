"""Replay providers. Choose one with REPLAY_PROVIDER in .env.

A provider is a module with a replays(fixtures, teams) function that follows ReplayProvider.
To add one, write a module in this package. Its file name, without .py, is the provider's name.
A provider is only imported once it's chosen, so a missing dependency in one can't stop the script.
Nothing checks providers against ReplayProvider, so it's the contract to write to.
"""

import pkgutil
from typing import Protocol


class ReplayProvider(Protocol):
    def replays(self, fixtures: list[dict], teams: dict[int, dict]) -> dict[int, str]:
        """Replay URLs for the fixtures this provider can find, keyed by FPL fixture id.

        fixtures and teams are FPL's own records. Fixtures without a replay are left out.
        Use timeouts on network calls, because rank.py waits for this to finish.
        Raising OSError, ValueError or ParseError is fine: rank.py reports it and ranks the gameweek
        without links. Other exceptions are treated as bugs and stop the script.
        """
        ...


PROVIDERS = sorted(module.name for module in pkgutil.iter_modules(__path__))
