# Approved local imagery directory

Stage only the imagery required by the Sudarshan demo.

Target pack: 30-38 image items.

Suggested grouping:
- SITE-A: 10 temporal observations for the primary construction-near-river case
- SITE-B: 7 observations for similar-site discovery
- SITE-C: 7 observations for seasonal/no-change suppression
- SITE-D: 6 observations for quality-confounded false-alarm handling
- Secondary query: optional small extension only when required

Recommended local naming:

`<asset_id>_<sensor>_<site>_<observation>.tif`

For every asset, add the required metadata to `data/demo_manifest.json` and record the licence/source/checksum.

Do not use online map tiles, cloud inference endpoints, or external APIs at runtime.
