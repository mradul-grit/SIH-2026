# Comprehensive Dataset Report: SIH-227

**Project**: Semantic Retrieval and Multi-Temporal Change Analysis of Satellite Imagery  
**Target Hardware**: Intel Core i5-12450H | 16 GB RAM | NVIDIA GeForce RTX 3050 (4 GB VRAM)  
**Storage Footprint**: 24.82 GB total across 66,794 image files / 19,490 bi-temporal pairs  

---

## 1. Executive Summary & Inventory Matrix

| Dataset Canonical Name | Source / Institution | Imagery Type / Sensor | Ground Resolution | Image Tile Size | Total Pairs | Ground Truth Format | Total Size |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **LEVIR-CD** | Beihang University (Chen & Shi) | Google Earth VHR Optical | 0.5 m/px | $1024 \times 1024$ | 637 pairs | Binary Mask PNG (0/255) | 2.30 GB |
| **LEVIR-CD+** | Beihang Univ. / IEEE GRSS | Google Earth VHR Optical | 0.5 m/px | $1024 \times 1024$ | 985 pairs | Binary Mask PNG (0/255) | 3.53 GB |
| **WHU-CD** | Wuhan Univ. (Ji, Wei & Lu) | Aerial Orthophotos (NZ) | 0.2 m/px | $512 \times 512$ & Mosaics | 1,950 pairs | GeoTIFF Raster + ESRI Shapefile | 7.10 GB |
| **S2Looking** | USTC (Shen, Xiong et al.) | Side-looking Satellites (GF-1/2, SV-1, BJ-2) | 0.5–0.8 m/px | $1024 \times 1024$ | 3,918 pairs* | Multi-mask (Change, Built, Demolished) | 8.64 GB |
| **SYSU-CD (Train)** | Sun Yat-sen Univ. (Shi et al.) | Aerial Optical RGB | 0.5 m/px | $256 \times 256$ | 12,000 pairs | Binary Mask PNG (0/255) | 3.25 GB |
| **AGGREGATE** | **5 Benchmarks** | **Optical Aerial & Satellite** | **0.2 – 0.8 m/px** | **$256 \times 256 \to 1024 \times 1024$** | **19,490 pairs** | **Binary + Semantic Sub-labels** | **24.82 GB** |

---

## 2. Dataset Deep-Dives

### 2.1. LEVIR-CD
* **Path**: `datasets/LEVIR CD`
* **Characteristics**:
  * Designed specifically for building change detection over 20 different urban and suburban regions across Texas, USA from 2002 to 2018.
  * Captures building emergence (new construction, suburban growth).
  * High fidelity $1024 \times 1024$ pixel pairs with crisp ground truth boundaries.
* **Splits**:
  * **Train**: 445 pairs (`train/A`, `train/B`, `train/label`)
  * **Validation**: 64 pairs (`val/A`, `val/B`, `val/label`)
  * **Test**: 128 pairs (`test/A`, `test/B`, `test/label`)
* **Integrity**: 100% complete, verified zero missing pairs.

### 2.2. LEVIR-CD+
* **Path**: `datasets/LEVIR-CD+/LEVIR-CD+`
* **Characteristics**:
  * Expanded benchmark with 985 bi-temporal pairs from challenging urban contexts, wide seasonal illumination differences, and complex background textures.
* **Splits**:
  * **Train**: 637 pairs
  * **Test**: 348 pairs
* **Integrity & Preprocessing Notes**:
  * Contains nested macOS metadata directories (`__MACOSX`, `.DS_Store`). 
  * The dataset adapter explicitly filters filenames to only match valid PNG files matching pattern `train_*.png` / `test_*.png`.

### 2.3. WHU-CD (Building change detection dataset_add)
* **Path**: `datasets/Building change detection dataset_add`
* **Characteristics**:
  * Covers Christchurch, New Zealand, following the severe February 2011 6.3-magnitude earthquake.
  * Time Period 1: 2012 (early post-disaster response and cleared building footprints).
  * Time Period 2: 2016 (4 years of comprehensive reconstruction and urban rebuilding).
  * Coordinate System: `NZGD_2000_New_Zealand_Transverse_Mercator` (EPSG:2193).
* **Components**:
  * `whole_image`: Full aerial orthophoto mosaics (5 train scenes, 5 test scenes) in 24-bit uncompressed GeoTIFF format.
  * `splited_images`: 1,260 train tiles and 690 test tiles pre-tiled to $512 \times 512$ non-overlapping tiles.
  * `shape file of the images`: Vector GIS building footprint polygons (`.shp`, `.dbf`, `.shx`, `.prj`) providing true georeferenced ground truth.

### 2.4. S2Looking
* **Path**: `datasets/S2Looking/S2Looking`
* **Characteristics**:
  * Multi-sensor satellite side-looking benchmark featuring GaoFen-1, GaoFen-2, SuperView-1, and BeiJing-2 satellites globally.
  * Contains significant off-nadir viewing angles (up to 35° tilt), creating building perspective displacement and roof/facade occlusions.
* **Ground Truth Annotations**:
  * `label`: Binary union of all building changes ($0$ or $255$).
  * `label1`: Newly constructed / added buildings.
  * `label2`: Demolished / removed buildings.
* **Split Counts & Anomaly Handling**:
  * **Test**: 1,000 complete pairs (`Image1`, `Image2`, `label`, `label1`, `label2`).
  * **Train**: `Image1`, `label`, `label1` contain 3,500 images, while `Image2` contains 2,918 images.
  * **Adapter Solution**: Dynamically compute intersection keys between `Image1` and `Image2`. Valid training pairs = 2,918.

### 2.5. SYSU-CD (Training Split)
* **Path**: `datasets/train`
* **Characteristics**:
  * Dense aerial orthophotos ($0.5$ m/px) covering diverse change categories: new urban developments, suburban expansion, vegetation changes, road construction, and earthworks.
  * Pre-tiled into $256 \times 256$ patches, ready for direct model consumption.
* **Splits**:
  * 12,000 bi-temporal pairs across `time1`, `time2`, and binary `label` ($0$ = unchanged, $255$ = change).

---

## 3. Data Leakage Prevention Protocol

Strict scene-level segregation is enforced across all loaders:
```
Original Physical Scenes
         │
         ├── Train Scenes (70% or official split) ──> Tiled Patches ──> Model Training
         ├── Val Scenes   (15% or official split) ──> Tiled Patches ──> Threshold Optimization & Early Stopping
         └── Test Scenes  (15% or official split) ──> Tiled Patches ──> Final Held-Out Evaluation
```
* **No random patch splitting**: Tiles originating from the same physical scene are never distributed across train and test partitions.
* **Preservation of Official Splits**: LEVIR-CD (445/64/128), LEVIR-CD+ (637/348), S2Looking (2918/1000), and WHU-CD (1260/690) official splits are maintained without contamination.

---

## 4. Hardware Budgeting for RTX 3050 (4 GB VRAM)

* **VRAM Capacity**: 4,094 MiB.
* **Max Target Allocation**: $\le 3,200$ MiB (leaving $\sim 800$ MiB safety buffer for Windows DWM and PyTorch workspace memory).
* **Patch Size**: $256 \times 256$ pixels.
  * ResNet-18 feature maps at $256 \times 256$:
    * Stage 1: $64 \times 128 \times 128 \approx 1.05$ MB
    * Stage 2: $64 \times 64 \times 64 \approx 0.26$ MB
    * Stage 3: $128 \times 32 \times 32 \approx 0.13$ MB
    * Stage 4: $256 \times 16 \times 16 \approx 0.07$ MB
    * Stage 5: $512 \times 8 \times 8 \approx 0.03$ MB
* **Batch Size**: $2$ (with Automatic Mixed Precision `torch.cuda.amp.autocast(dtype=torch.float16)`).
* **Gradient Accumulation**: 4 steps (effective batch size = 8).
* **Disk-to-RAM I/O**: Lazy generators opening images upon batch indexing. Zero entire-dataset pre-loading.
