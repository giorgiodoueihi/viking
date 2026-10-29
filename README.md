# viking

Ranks the latest Premier League gameweek from most to least worth watching, without spoiling any results.

Match data comes from the Fantasy Premier League API. [TypeSafe's Jev](https://typesafe.ai) scores each match, and you only see the order.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
echo "TYPESAFE_API_KEY=your-key" > .env
```

To add a replay link to each match, write a provider and choose it in `.env` too. A provider is a module in `providers/` with a `replays(fixtures, teams)` function that returns replay URLs keyed by FPL fixture id. Its name is its file name, so `providers/example.py` is chosen like this:

```bash
echo "REPLAY_PROVIDER=example" >> .env
```

See `ReplayProvider` in [providers/__init__.py](providers/__init__.py) for the details.

## Usage

```bash
.venv/bin/python rank.py
```

Each ranking is saved to `rankings/gwN.txt`, and a gameweek that's already been ranked is skipped. Use `--gameweek N` to rank a specific round.
