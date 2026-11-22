# THE WORLD — 21 November 2026

An entry for the `news-image-20261121` bounty: one image that sums up the world
news of Saturday 21 November 2026.

## The image

`image.png` is a 1024 × 1024 PNG (about 180 KiB) drawn to look like the front
page of a newspaper, because the judge is comparing images and a front page
shows and says the news at the same time.

- **Masthead:** `THE WORLD`, with the date bar `SATURDAY 21 NOVEMBER 2026`.
- **Lead story:** *IRAN STRIKES TWO US SITES IN BAHRAIN* — a deck and two short
  columns, beside a drawn map of the Gulf: Iran across the north, Bahrain
  marked with two strike stars, a dashed shipping lane, and two tankers burning
  near the Strait of Hormuz.
- **Nine more panels**, each with flag colours, a section kicker, a bold
  headline and a one-line summary:
  - Boy, 7, and paramedic killed in Kryvyi Rih; missiles also hit Poland
  - Russian cargo ship *Sparta II* ablaze in the Gulf of Finland
  - Mexico captures *El Chapo Isidro*, an FBI most-wanted cartel boss; 11 dead
  - COP31 talks in Antalya run past deadline
  - Nasdaq erases its 2026 gains; Nvidia down 14% on a reported SEC probe
  - Trump, Xi and Putin meet at APEC in Shenzhen
  - Bred mosquitoes cut child dengue cases in Brazil by 69%
  - Magnitude 6.8 earthquake shakes the Andes in Peru
  - Bitcoin slides to $55,300, then rebounds above $60,000

Everything in the image is drawn from scratch with Pillow; no stock art, no
downloaded pictures, no invented stories.

## Running it

The entry itself needs nothing but Python 3 and its standard library:

```sh
python3 main.py
```

That copies the finished `image.png` to `/output/entry.png`, creating `/output`
if it does not exist. The copy is byte-for-byte, so repeated runs produce
identical output. There is no network access, no randomness and no clock read
anywhere in the run.

## Regenerating the artwork

`gen_image.py` draws the page. It needs Pillow:

```sh
python3 gen_image.py   # rewrites image.png
```

It measures every block before drawing it and stops with an error rather than
overflowing a panel, so a successful run means the text fits and nothing
collides.

## Layout

```
main.py        entry point: copies image.png to /output/entry.png
image.png      the finished front page, 1024 x 1024
gen_image.py   the drawing script (Pillow, development only)
```

## Licence

MIT — see `LICENSE`.
