# Landscape 3D/CAD WebGL Engine & Procedural Phenology Patterns

---

## 🌲 Overview & Architecture
This reference encapsulates core architectural patterns for browser-based 2D/3D landscape CAD applications combining centimeter-precision 2D drafting with high-performance 60 FPS WebGL visualization and reactive agronomic/normative calculation engines.

```
+-------------------------------------------------------------------------------------------------+
|                              Hybrid Landscape CAD Architecture                                  |
+-------------------------------------------------------------------------------------------------+
| [2D Planar CAD Engine]  Maker.js (Centimeter snaps, DXF export) + Paper.js + Clipper2          |
| [3D WebGL Viewport]     Three.js (WebGL 2.0 / WebGPU) + Dual-Tier Plant Instancing              |
| [Macro LOD 0]           THREE.InstancedMesh 2.5D Billboards (1-3 draw calls for 1,000+ plants)   |
| [Micro LOD 1 / 2]       @dgreenheck/ez-tree procedural meshes (glTF export, wind vertex shaders)|
| [Seasonal Engine]       12-Month Phenology GLSL Shaders (dormancy, bloom alpha, autumn senescence)|
| [Solar Simulation]      SunCalc astronomical vector positioning (Lat 44°–52° N for Ukraine)    |
| [Relief & Terrain]      three-geo (Satellite DEM tiles) / THREE.Terrain (Local TIN mesh)        |
| [Normative Audit]       ДБН В.2.2-12:2019 Table 9.1 Spatial Clearances & Collision Detection    |
| [Reactive BoQ Bridge]   JSON Canvas 1.0 Bi-Directional Sync & ДСТУ Б А.2.4-4:2009 Spec Engine   |
| [Drawing Album Engine]  Pure-Python DXF CAD R12 & Vector SVG Sheets (ДСТУ Б А.2.4-4:2009 Form 3)|
| [Irrigation Hydraulics] Hazen-Williams Engine, PE-100 Auto-Sizing & TDH Pump Selection          |
+-------------------------------------------------------------------------------------------------+
```

---

## 1. 2.5D Plant Billboard Instancing (`plantSpriteRenderer`)

To render 1,000+ shrubs and perennials without GPU overload:
1. Use `THREE.InstancedMesh` with a quad geometry ($2$ triangles).
2. Vertex shader implements cylindrical camera-facing alignment (locking rotation to the world $Y$-axis to prevent awkward tilt when camera pitches):
```glsl
vec3 look = cameraPosition - instancePosition;
look.y = 0.0;
look = normalize(look);
vec3 right = normalize(cross(vec3(0.0, 1.0, 0.0), look));
vec3 up = vec3(0.0, 1.0, 0.0);
vec3 transformed = position.x * right + position.y * up;
```
3. Use packed WebP texture atlases (`leaf-atlas.webp`, `flower-atlas.webp`) with per-instance UV offset attributes (`attribute vec4 uvOffsetScale`) to draw distinct botanical cultivars in a single draw call.

---

## 2. 4-Season Phenology Shader (`season3d`)

Dynamic continuous phenology across month parameter $t \in [0.0, 11.99]$:
- **Winter Dormancy ($t \in [11, 2]$)**: Deciduous plants discard foliage via alpha-test thresholding or UV shift to bare branches. Conifers shift towards desaturated dark blue-green ($\Delta \text{Hue} \approx -20^\circ$).
- **Spring Leaf-Out ($t \in [3, 5]$)**: Foliage scales from $0.1 \to 1.0$; color shifts from lime-yellow to emerald.
- **Bloom Window ($t \in [t_{\text{start}}, t_{\text{end}}]$)**: Secondary alpha mask activates blossom texture layer with cultivar-specific pigment blending.
- **Autumn Senescence ($t \in [9, 10]$)**: Chlorophyll decay calculation raises carotenoid/anthocyanin tint (yellow/orange/crimson) before triggering dormancy alpha fade.

---

## 3. Solar Raycasting & Shadow Projection (`SunCalc`)

- Integration with Three.js `DirectionalLight`:
```typescript
import SunCalc from 'suncalc';

export function updateSunPosition(
  light: THREE.DirectionalLight,
  date: Date,
  lat: number, // 44.0 to 52.0 for Ukraine
  lon: number,
  radius: number = 200
) {
  const { altitude, azimuth } = SunCalc.getPosition(date, lat, lon);
  // Transform horizontal coordinates to Three.js Cartesian (Y-up)
  const phi = Math.PI / 2 - altitude;
  const theta = azimuth - Math.PI / 2;

  light.position.set(
    radius * Math.sin(phi) * Math.cos(theta),
    Math.max(radius * Math.cos(phi), 0.01),
    radius * Math.sin(phi) * Math.sin(theta)
  );
  light.target.position.set(0, 0, 0);
  light.target.updateMatrixWorld();
}
```
- Real-time scrubbing across hours and calendar months enables solar exposure analysis (Full Sun $>6$h vs Full Shade $<3$h per bed).

---

## 4. 2D Precision CAD Drafting (`Maker.js` + `Paper.js` + `Clipper2`)

- **Coordinate Standard**: 1 world unit = 1.0 meter (or centimeter grid with 0.01 scale factor).
- **Underlay Alignment**: 2-point reference calibration transforms scanned BTI / cadastral maps:
  $$S = \frac{\text{Distance}_{\text{meters}}}{\text{Distance}_{\text{pixels}}}$$
- **Boolean Operations**: Clipper2 handles multi-hole garden beds (lawn polygon minus mulch bed minus patio) without degenerate zero-area faces.
- **CAD Export**: Native DXF generation via `makerjs.exporter.toDXF()` for on-site construction teams.

---

## 5. Procedural Vegetation & DEM Elevation
- `@dgreenheck/ez-tree`: Generates procedural trunk and branch geometry using space colonization L-systems, equipped with vertex wind displacement and LOD mesh export (glTF/USDZ).
- `three-geo`: Ingests Mapbox / SRTM RGB elevation tiles for regional estates and hillside micro-relief.
- `THREE.Terrain`: High-speed local TIN generation for plots $< 1$ hectare with contour line shader support.

---

## 6. Spatial Normative Validation (ДБН В.2.2-12:2019 Table 9.1)

Automated live clearance detection prevents municipal and construction compliance violations:
1. **Building Clearances**:
   - Tree axis to exterior building wall: $\ge 5.0\text{ m}$ (risk of foundation heave, structural root damage, moisture shadowing).
   - Shrub axis to building wall: $\ge 1.5\text{ m}$.
2. **Property Boundaries & Fences**:
   - Tree axis to boundary / fence: $\ge 2.0\text{ m}$ (prevent neighbor boundary tree disputes and shadow overcasting).
   - Shrub axis to fence: $\ge 1.0\text{ m}$.
3. **Crown Collision & Over-Densification**:
   - Spacing between mature trees: $d \ge 0.8 \times (r_1 + r_2)$ where $r_1, r_2$ are mature crown radii.
   - Violations flag canopy competition and root-zone starvation before planting.
4. **Agronomic Mismatch Detection**:
   - Mismatch between parcel soil pH (e.g. pH $> 6.5$) and acidophilic plants (*Rhododendron*, *Hydrangea* requiring pH $4.5\text{--}5.5$).
   - Insolation conflicts (planting shade-tolerant species under full sun or vice versa).

---

## 7. Reactive Canvas BoQ & ДСТУ Б А.2.4-4:2009 Bridge

The reactive bridge (`LandscapeCanvasBridge`) maintains bi-directional synchronization between interactive canvas nodes and the backend calculation engine:
1. **JSON Canvas 1.0 Protocol**:
   - Nodes represent plants (`plant_id`, mature spread, root system spec) or obstacles (buildings, fences, paving polygons).
   - Edges define underground utility lines or irrigation loops.
2. **Sub-5ms Drag & Drop Recompute**:
   - Dragging a tree node recalculates Euclidean distances against all active obstacles and adjacent trees.
   - Emits delta payload containing: updated coordinates, normative violation warnings (`DbnViolation`), updated assortative schedule (Відомість елементів озеленення), and full Bill of Quantities (BoQ) in local currency.

---

## 8. AI Vision Orthophoto Ingestion & Monocular Terrain Relief (SAM 2 & Depth Anything V2)

Automated raster-to-CAD synthesis converts satellite orthophoto and drone imagery into calibrated canvas nodes:
1. **Ramer-Douglas-Peucker (RDP) Contour Simplification**:
   - Compresses noisy pixel-level segmentation masks from SAM 2 into clean polygon vertices with configurable tolerance $\epsilon$:
   - Perpendicular distance test preserves salient corners while reducing polygon vertex count by $>60\%$.
   - Retains metric Shoelace area: $A = \frac{1}{2} |\sum_{i=0}^{n-1} (x_i y_{i+1} - x_{i+1} y_i)|$.
2. **Metric Anchor Calibration**:
   - Calibrates pixel space to real-world meters using known cadastral parcels (State Land Cadastre ДЗК) or verified building wall measurements:
     $$\text{meters\_per\_pixel} = \sqrt{\frac{\text{Cadastral Area } (\text{m}^2)}{\text{Pixel Polygon Area } (\text{px}^2)}}$$
3. **Least-Squares Plane Estimation & Stormwater Runoff (ДСТУ-Н Б В.1.1-27:2010)**:
   - Fits best-fit 3D plane $z = ax + by + d$ from monocular DEM/heightmap points.
   - Surface normal vector: $\vec{N} = \frac{(-a, -b, 1)}{\sqrt{a^2 + b^2 + 1}}$.
   - Slope angle & percentage: $\theta = \arccos(N_z)$, $\text{Slope}_{\%} = \tan(\theta) \times 100\%$.
   - Surface drainage runoff vector: $\vec{D} = (-N_x, -N_y)$ (downhill gradient direction).
   - High-risk erosion warning triggered when $\text{Slope}_{\%} \ge 15.0\%$.
4. **Instant Canvas Synthesis**:
   - Detected site classes (`BUILDING`, `HARDSCAPE`, `EXISTING_TREE`, `BOUNDARY_FENCE`) map directly to `LandscapeCanvasState` and feed the reactive BoQ engine on load.

---

## 9. Automated Drawing Album Generation (ДСТУ Б А.2.4-4:2009 Form 3 & CAD DXF Export)

Architectural drawings require strict compliance with Ukrainian construction standards (SPDS / ДСТУ):
1. **Standard Form 3 Title Block (Основний напис за Формою 3)**:
   - Dimensions: $185\text{ mm} \times 55\text{ mm}$ placed at the bottom-right corner of standard sheets (A3 Landscape: $420\text{ mm} \times 297\text{ mm}$).
   - Left margin $20\text{ mm}$ for binding; top, right, bottom margins $5\text{ mm}$.
   - Grid partitions: stage (`Стадія`: П/Р/РП), sheet index (`Аркуш`), total sheets (`Аркушів`), organization (`Організація`), designer roles (`Розробив`, `Перевірив`, `ГІП/ГАП`).
2. **Multi-Sheet Album Architecture**:
   - **Sheet 1**: Генеральний план (Master Site Plan) with boundary markers, hardscape zoning, north arrow, and metric scale bar.
   - **Sheet 2**: Дендроплан та посадкове креслення (Dendroplan & Planting Layout) with numeric plant tagging, dimensional offset ties to hardscape/boundaries, and planting pit specifications.
   - **Sheet 3**: Відомість елементів озеленення (Planting Schedule / BoQ) with botanical Latin/UA nomenclature, root ball specifications (C7.5 / WRB), and planting density.
3. **Pure-Python DXF CAD R12 Generator**:
   - Eliminates heavy native C-libraries (`ezdxf`, `libredwg`) for instant in-process execution.
   - Emits pure ASCII DXF with minimal standard sections: `HEADER` ($INSUNITS=6$ for meters), `TABLES` (layers: `0`, `BOUNDARIES`, `BUILDINGS`, `TREES`, `SHRUBS`, `DIMENSIONS`), `BLOCKS`, and `ENTITIES` (`LINE`, `LWPOLYLINE`, `CIRCLE`, `TEXT`).

---

## 10. Landscape Irrigation Hydraulics & Zoning Engine (ASABE & ДБН В.2.5-74:2013)

Automated hydraulic design transforms garden layouts into balanced micro-irrigation networks:
1. **Catalog & Nozzle Characteristics**:
   - Equipment profiles: Rotary nozzles (Hunter MP Rotator 1000/2000/3000), Spray nozzles (Rain Bird HE-VAN), Gear-driven Rotors (Hunter PGP Ultra, Rain Bird 5000+), Drip tubing (16mm inline emitter $2.3\text{ L/h}$).
   - **Strict Nozzle Isolation Invariant**: Never mix rotary nozzles with spray heads or drip lines on the same valve zone due to disparate precipitation rates ($10\text{--}15\text{ mm/h}$ vs $40\text{--}50\text{ mm/h}$).
2. **Hazen-Williams Friction Loss Equation**:
   $$h_f = 10.674 \times \frac{L \times Q^{1.852}}{C^{1.852} \times D^{4.8704}}$$
   - $h_f$: Head loss due to friction ($\text{m}$ of water column).
   - $L$: Pipe segment length ($\text{m}$).
   - $Q$: Volumetric flow rate ($\text{m}^3/\text{s}$).
   - $C$: Roughness coefficient ($C = 150$ for HDPE PE100 polyethylene).
   - $D$: Internal pipe diameter ($\text{m}$).
3. **PE-100 Auto-Sizing & Velocity Invariant**:
   - Standard SDR11/SDR13.6 HDPE pipe series: DN20 ($D_{in}=16.0\text{mm}$), DN25 ($D_{in}=20.4\text{mm}$), DN32 ($D_{in}=26.0\text{mm}$), DN40 ($D_{in}=32.6\text{mm}$), DN50 ($D_{in}=40.8\text{mm}$).
   - **Velocity Safety Invariant**: Pipe velocity $v = \frac{4Q}{\pi D^2} \le 1.8\text{ m/s}$ (recommended $1.2\text{--}1.5\text{ m/s}$) to eliminate water hammer (гідравлічний удар) and pipe fatigue.
4. **Zoning Bin-Packing & TDH Pump Selection**:
   - Zones partitioned such that total zone flow $Q_{\text{zone}} \le Q_{\text{source\_max}}$ (e.g., $2.5\text{ m}^3/\text{h}$).
   - Critical path pressure drop determines Total Dynamic Head (TDH):
     $$H_{\text{pump}} = (P_{\text{nozzle\_req}} + h_{f,\text{pipe}} + \Delta Z_{\text{elev}} + h_{\text{valves\_fittings}}) \times 1.15$$
   - Hydraulic power estimate: $P_{\text{hyd}} = \frac{\rho \cdot g \cdot Q \cdot H}{3600 \cdot \eta \cdot 1000}\text{ kW}$ ($\eta \approx 0.65$).
