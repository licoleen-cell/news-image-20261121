[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/licoleen-cell/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/licoleen-cell/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

[Sum up 21 November's world news in one image](https://make.fun/bounty/news-image-20261121)

# News v3 — Candidate A: Pictogram Grid

A one-image "front page" for Saturday 21 November 2026: a 2×4 grid of eight
stories, each pairing a large flat pictogram (drawn with Pillow shapes, no
photography) with a short headline and one fact line.

## Files

| File | Purpose |
| --- | --- |
| `gen_image.py` | Renders `image.png` (1024×1024) with Pillow. |
| `main.py` | Standard library only; copies `image.png` to `/output/entry.png`. |
| `texts.txt` | The eight headlines (`H:`) and fact lines (`S:`), one per line. |
| `image.png` | The rendered front page. |

## Run

```sh
python3 gen_image.py   # writes image.png
python3 main.py        # copies it to /output/entry.png
```

`main.py` copies bytes, so repeated runs are identical. `gen_image.py` is
deterministic too: fixed coordinates, fixed fonts, no randomness, and text
drawn on whole pixels so the same input always yields the same PNG.

## Design

- **Masthead** — the date set as large as the page width allows, over a
  double rule.
- **Grid** — two columns, four rows. Row heights are solved from the content:
  the largest headline size whose four rows fit the page wins, so a card with
  a three-line headline claims the extra height instead of shrinking every
  other card's type.
- **Icons** — a missile and fireball, a burning ship, a globe with an alarm,
  a Bitcoin mark on a falling chart, a mosquito, a collapsing building,
  handcuffs, and a seismic shockwave. Drawn as vector shapes at 4× and
  downsampled, so edges stay clean at any size.
- **Type** — headline size comes from a fixed ladder (62/56/50/44 px), which
  keeps neighbouring cards related while letting short headlines run large.
  Fact lines are 28 px. Every headline reads back correctly through OCR at
  256, 384 and 512 px.
- **Fact lines** — "IRGC claims" keeps the Iran story attributed, and the
  Friday events carry their day.

## Facts

Every figure comes from the brief and is unchanged: 16 crew, 69%, $55,300,
$60,000, magnitude 6.7, 2 dead in Kryvyi Rih, 11 dead in the raid.

## Licence

MIT. See `LICENSE`.
