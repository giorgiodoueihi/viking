# viking

Ranks the latest Premier League gameweek from most to least worth watching, without spoiling any results.

Match data comes from the Fantasy Premier League API. [TypeSafe's Jev](https://typesafe.ai) scores each match, and you only see the order.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
echo "TYPESAFE_API_KEY=your-key" > .env
```

## Usage

```bash
.venv/bin/python rank.py
```

Each ranking is saved to `rankings/gwN.txt`, and a gameweek that's already been ranked is skipped. Use `--gameweek N` to rank a specific round.
