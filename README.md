# dreadpirateduppie.com — static archive

A static rebuild of [dreadpirateduppie.com](https://www.dreadpirateduppie.com),
matching the original's terminal look: black ground, `#00FF07` phosphor green,
`#FA0000` alert red, Courier New chrome, Matrix rain and the
`> _STANDING_ON_BUSINESS_SINCE_2025.` tickers.

14 posts, real publication dates, categories and read times.

## Where the data comes from

- **Metadata** — titles, dates, categories, read times, excerpts and cover
  images come from the site's own RSS feed (`/blog-feed.xml`).
- **Post bodies** — scraped markdown in `content/posts/`.
- **Images** — resized to 1600px and converted to webp.

Four posts were subscriber-only on the original. The build detects the paywall
marker, shows the feed excerpt as the opening, and links back to the source.

## Layout

```
content/posts/   source markdown
assets/img/      webp images + author avatar
assets/css/      stylesheet
assets/js/       matrix rain + category filter
build.py         the generator
index.html       generated
posts/*.html     generated
```

## Building

```sh
python3 build.py
```

No dependencies — standard library only. The `POSTS` table at the top of
`build.py` holds the feed-derived metadata; everything else is derived from the
markdown.
