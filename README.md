[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/licoleen-cell/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/licoleen-cell/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

[Sum up 21 November's world news in one image](https://make.fun/bounty/news-image-20261121)

# News v3 — Candidate D: Pictogram Grid, 10 Stories

A one-image "front page" for Saturday 21 November 2026: a 2×5 grid of ten
stories, each pairing a large flat pictogram (drawn with Pillow shapes, no
photography) with a short headline and one fact line. It combines the full
coverage of the v2 front page (all ten stories, including markets and APEC)
with the large readable type of the pictogram-grid design.

## Files

| File | Purpose |
| --- | --- |
| `gen_image.py` | Renders `image.png` (1024×1024) with Pillow. |
| `main.py` | Standard library only; copies `image.png` to `/output/entry.png`. |
| `texts.txt` | OCR measurements at 256/384/512 px and the determinism check. |
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

- **Dateline** — "SATURDAY 21 NOVEMBER 2026" set as large as the page width
  allows, over a red rule.
- **Grid** — two columns, five rows, ten stories. Headlines 52 px, fact lines
  38–40 px, 92 words in total.
- **Icons** — a missile and fireball, a teddy bear, a burning ship,
  handcuffs, a globe with an alarm, a falling chart, three figures at a
  summit, a mosquito, a seismic shockwave, and a Bitcoin mark. Drawn as
  vector shapes at 4× and downsampled, so edges stay clean at any size.
- **Readability** — tesseract word coverage: 58.7% @256 px, 94.6% @384 px,
  97.8% @512 px (v2's grid headlines were 1.8% @256 px).

## Facts

Every figure comes from verified reporting of 21 November 2026: IRGC claims
US radars hit in Bahrain (Bahrain: site ablaze, no one hurt); boy, 7, and a
paramedic killed in Kryvyi Rih on Friday; Sparta II ablaze, 16 crew saved;
El Chapo Isidro captured, Friday raid, 11 dead; COP31 past deadline,
deadlocked on fossil fuels; Nasdaq erases 2026 gains (S&P -3.7%, Nasdaq
-5.3%); Trump, Xi and Putin at APEC, Nov 19; Wolbachia cuts dengue 69% in a
Brazil trial; magnitude 6.7 quake in Junín, Peru, on Friday; Bitcoin $55,300
low, back above $60,000.

## Licence

MIT. See `LICENSE`.
