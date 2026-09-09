# Data Contract

Each indexed tile should preserve, at minimum:

```text
tile_id
source_scene
sensor
acquisition_time
geometry
crs
resolution
source_file
processing_version
quality_flags
embedding_reference
```

Never discard source-scene provenance during preprocessing.
