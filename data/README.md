# Earth Observation Datasets & Catalogs (SIH-26227)

This directory manages dataset manifests, registry definitions, and metadata for the 5 benchmark satellite change detection datasets unified in this project.

---

## 1. Unified Dataset Inventory

| Dataset | Modality / Sensor | Ground Sampling Dist. (GSD) | Total Pairs | Disk Size | Canonical Classes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **LEVIR-CD** | Google Earth Optical VHR | 0.5 m / px | 637 pairs | 2.30 GB | `no_change`, `building_change` |
| **LEVIR-CD+** | Google Earth Optical VHR | 0.5 m / px | 985 pairs | 3.53 GB | `no_change`, `building_change` |
| **WHU-CD** | Christchurch Aerial Orthophoto | 0.2 m / px | 1,950 pairs | 7.10 GB | `no_change`, `building_change` |
| **S2Looking** | GF-1, GF-2, SuperView-1, BJ-2 | 0.5 - 0.8 m / px | 3,918 pairs | 8.64 GB | `no_change`, `new_building`, `demolished` |
| **SYSU-CD** | Aerial Optical RGB | 0.5 m / px | 12,000 pairs | 3.25 GB | `no_change`, `change` |
| **Total** | **Multi-Sensor Optical & Aerial** | **0.2 - 0.8 m / px** | **19,490 pairs** | **24.82 GB** | **Binary & Multi-Task Semantics** |

---

## 2. Directory Layout & Storage Protocol

Raw raster GeoTIFF and PNG files should be placed in the `datasets/` root folder (gitignored):

```text
datasets/
├── LEVIR CD/
│   ├── train/ (A, B, label)
│   ├── val/   (A, B, label)
│   └── test/  (A, B, label)
├── LEVIR-CD+/
│   └── LEVIR-CD+/ (train, test)
├── Building change detection dataset_add/
│   └── 1. The two-period image data/ (Christchurch WHU)
├── S2Looking/
│   └── S2Looking/ (train, test with multi-mask labels)
└── train/
    └── (SYSU-CD 12,000 tiles: time1, time2, label)
```

---

## 3. Metadata Files

* [`data/dataset_inventory.json`](file:///run/media/mayanksoni/Arise/natraj26227/data/dataset_inventory.json): Full technical specification, split counts, sensor parameters, CRS definitions, and hardware targets.
* [`data/dataset_manifest.json`](file:///run/media/mayanksoni/Arise/natraj26227/data/dataset_manifest.json): Checksum and file-level integrity registry.
* [`data/dataset_report.md`](file:///run/media/mayanksoni/Arise/natraj26227/data/dataset_report.md): In-depth exploratory data analysis (EDA) report.
