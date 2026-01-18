# Auto Portfolio Builder (Google Play + App Store) 🎮

This repository automatically generates my **game portfolio** from store data (Google Play + Apple App Store) and publishes it as a website via **GitHub Pages**.

➡️ **Live portfolio:** <https://username-dorf.github.io/google-play-apps-parser/>

---

## What is this?

A lightweight pipeline that:
1. reads a list of apps (`data/packages.json`)
2. fetches public metadata from the stores (title, genre, release date, links, icons, screenshots)
3. generates:
   - `apps.xlsx` (source table)
   - a static website (`/site`) + assets
4. deploys the website to **GitHub Pages** using GitHub Actions.

This makes the portfolio always up-to-date and easy to maintain.

---

## How it works

### Data source
- Edit: `data/packages.json`
- Each entry may contain:
  - `google` — Android package id (e.g. `com.company.game`)
  - `apple` — App Store track id (e.g. `1495148649`)

Apps may exist in only one store — the site will show only the available store button(s).

---

## Running locally

### Prerequisites
- Python 3.9+ recommended

### Install
```bash
pip install -r requirements.txt
python runner.py data/packages.json
python html_creator.py
```
