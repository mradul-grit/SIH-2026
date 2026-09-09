# API Contract

## POST /api/search/text

### Request

```json
{
  "query": "newly built structures near a river",
  "aoi": null,
  "date_from": "YYYY-MM-DD",
  "date_to": "YYYY-MM-DD",
  "sensor": null,
  "top_k": 10
}
```

### Response

```json
{
  "results": [
    {
      "tile_id": "tile_001",
      "score": 0.91,
      "confidence": 0.88,
      "geometry": {},
      "acquisition_time": "YYYY-MM-DDTHH:MM:SS",
      "sensor": "Sentinel-2",
      "source_scene": "scene_id",
      "processing_version": "v0.1"
    }
  ]
}
```

## POST /api/search/image

Input: image/tile + optional filters.

Output: same ranked result schema.

## POST /api/change/analyze

### Request

```json
{
  "aoi": {},
  "date_from": "YYYY-MM-DD",
  "date_to": "YYYY-MM-DD"
}
```

### Response

```json
{
  "changes": [],
  "confidence": 0.0,
  "earliest_supported_observation": null,
  "provenance": []
}
```

## Contract Rule

Any breaking schema change requires:
1. Issue
2. Team agreement
3. Version bump
4. Backend + frontend + tests updated together
