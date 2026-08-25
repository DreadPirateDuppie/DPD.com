# dreadpirateduppie.com — archive

A static archive of the writing originally published at
[dreadpirateduppie.com](https://www.dreadpirateduppie.com): 12 posts,
~17,000 words, 29 images, no trackers, no JavaScript beyond a scroll bar.

## Layout

```
content/posts/   source markdown (scraped from the original site)
assets/img/      images, resized to 1600px and converted to webp
assets/css/      the stylesheet
build.py         the generator
index.html       generated
posts/*.html     generated
```

## Building

```sh
python3 build.py
```

No dependencies — standard library only. Post titles, deks and tags live in
the `POSTS` table at the top of `build.py`; everything else is derived from the
markdown. Posts that were subscriber-only on the original site are detected by
their paywall marker and rendered as excerpts that link back to the source.
