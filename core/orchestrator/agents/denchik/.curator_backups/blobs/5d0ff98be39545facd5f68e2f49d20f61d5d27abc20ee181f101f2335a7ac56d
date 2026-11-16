<!-- --- DNK-MRH-HEADER ---
mrh_id: "core/orchestrator/agents/denchik/skills/software-development/canvas-engine-architecture/references/landscape_lighting_and_master_estimator_patterns.md"
purpose: "Engineering patterns for landscape exterior lighting (12V SELV voltage drop, Multi-Tap boost, IP68 invariant), Master Commercial BoQ Estimator, and verified FastAPI E2E test client contracts."
canonical_source: true
alters_files: []
triggers_tasks: []
status: "Active"
version: "1.1.0"
updated_at: "2026-10-30"
author: "DNK-e.com Maksym & Denchik"
--- END DNK-MRH-HEADER -->

# 💡 Landscape Exterior Lighting & Master Commercial BoQ Estimator Patterns

## 1. Exterior Low-Voltage Lighting (12V/24V SELV & 220V Mains)

### A. Voltage Drop Formulation (Ohm's & Pouillet's Laws)
For a single-phase two-wire circuit (out and return):
$$\Delta U = 2 \cdot I \cdot R = 2 \cdot I \cdot \frac{\rho_{Cu} \cdot L}{S}$$
- $\rho_{Cu} = 0.0175\ \Omega\cdot\text{mm}^2/\text{m}$ (standard copper resistivity at $20^\circ\text{C}$).
- $I = \frac{P}{V}$ (amperes).
- $L$ = one-way distance in meters from power source/transformer to fixture load center.
- $S$ = copper conductor cross-sectional area ($\text{mm}^2$).

### B. Standard Conductor Sizing & Safe Percentage Limits
- **12V Low Voltage Lines**: Maximum allowable drop $\Delta U \le 7.0\% - 8.0\%$ ($0.84\text{V} - 0.96\text{V}$) to ensure LED chips operate without flickering, driver burnout, or color temperature shifts.
- **Copper Cable Gauges**: $0.75, 1.0, 1.5, 2.5, 4.0, 6.0, 10.0, 16.0\ \text{mm}^2$.
- **Multi-Tap Transformers**: When runs exceed 30m, voltage drop lowers terminal voltage below 11.0V. Multi-tap secondary windings (12V, 13V, 14V, 15V) boost output to compensate for feeder loss:
  $$V_{\text{tap}} = \text{argmin}_{T \in [12, 13, 14, 15]} (T - \Delta U \ge 11.2\text{V})$$

### C. Normative Water Safety Invariant (ДБН В.2.5-28:2018 / ПУЕ)
- Underwater spotlights (`FixtureType.UNDERWATER`) and pool fixtures MUST strictly enforce:
  1. Operating voltage $\le 24\text{V}$ (SELV).
  2. Ingress protection rating strictly `IP68`.
  3. Galvanically isolated transformer located outside Zone 0/Zone 1 ($\ge 2.0\text{m}$ from water edge).

---

## 2. Master Commercial BoQ & Financial Estimator (Ukrainian Market Standard)

### A. Hierarchical 5-Domain Structure
1. **Hardscape (Тверді покриття та мощення)**:
   - Base layer preparation (щебінь 20-40, відсів, пісок, трамбування віброплитою).
   - Pavers (тротуарна плитка Старе місто, Колормікс 60мм).
   - Concrete-encased park borders (бордюр парковий на бетонний замок).
2. **Planting (Озеленення та дендрологія)**:
   - Plant material priced from Ukrainian Nursery Association (АВПМУ) catalog.
   - Differentiated planting labor: Deciduous/conifer trees (with anchoring stakes), shrubs, perennials/ornamental grasses.
3. **Lawn (Газони)**:
   - Rolled turf (рулонний газон 100% мятлик) vs Seeded lawn (Barenbrug/DLF).
4. **Irrigation (Автоматичне зрошення)**:
   - Hunter Pro-Spray / MP Rotators with swing joints, HDPE PN10 pipes, solenoid valves, Hunter X-Core controller, pump station.
5. **Lighting (Ландшафтне освітлення)**:
   - Spotlights, pathway bollards, copper cables in corrugated conduit, Multi-Tap transformer with astronomical timer.

### B. Mathematical Multipliers & Cost Aggregation
- **Split Accounting**:
  $$\text{Item Total} = Qty \cdot (\text{Material Price} + \text{Labor Price})$$
- **On-Site Logistics & Delivery**: $3\%$ of base subtotal.
- **Contingency Reserve (Непередбачені витрати)**: $5\%$ of base subtotal.
- **Overhead & Contractor Margin (Загальновиробничі витрати)**: $5\%$ of base subtotal.
- **Dynamic Multi-Currency Summary**:
  $$\text{Grand Total EUR} = \frac{\text{Grand Total UAH}}{\text{EUR Rate}},\quad \text{Grand Total USD} = \frac{\text{Grand Total UAH}}{\text{USD Rate}}$$

---

## 3. Verified FastAPI E2E Test Contracts & Payloads

When executing live tests via `fastapi.testclient.TestClient(app)` against `/api/v1/landscape/`, adhere strictly to these schema contracts:

### A. Irrigation Calculation (`POST /api/v1/landscape/irrigation/calculate`)
```python
client.post(
    "/api/v1/landscape/irrigation/calculate",
    json={
        "project_id": "PRJ-001",
        "zones": [
            {
                "zone_id": "zone_lawns_01",
                "zone_name": "Парадний газон",
                "nozzle_model": "Hunter MP2000",
                "sprinkler_count": 6,
                "flow_rate_per_nozzle_m3h": 0.16,
                "target_pressure_bar": 2.8,
                "pipe_internal_diameter_mm": 26.0,
                "total_pipe_length_m": 45.0,
                "elevation_change_m": 0.5,
            }
        ],
        "water_source": {
            "source_type": "well",
            "static_pressure_bar": 3.0,
            "max_flow_m3h": 3.5,
        },
    },
)
```
- **Response keys**: `summary`, `zones_calculated`, `pump_requirement` (`required_flow_m3h`, `total_dynamic_head_bar`).

### B. Exterior Lighting (`POST /api/v1/landscape/lighting/calculate`)
```python
client.post(
    "/api/v1/landscape/lighting/calculate",
    json={
        "circuit_name": "C1_Garden_Path",
        "supply_voltage_v": 12.0,
        "cable_section_mm2": 2.5,
        "cable_length_m": 24.6,
        "fixtures": [
            {
                "fixture_id": "f1",
                "fixture_type": "path_light",
                "wattage": 5.0,
                "operating_voltage_v": 12.0,
                "cable_length_m": 5.0,
            },
            {
                "fixture_id": "f2",
                "fixture_type": "spotlight",
                "wattage": 10.0,
                "operating_voltage_v": 12.0,
                "cable_length_m": 12.0,
            },
            {
                "fixture_id": "f3",
                "fixture_type": "uplight",
                "wattage": 10.0,
                "operating_voltage_v": 12.0,
                "cable_length_m": 20.0,
            },
        ],
    },
)
```
- **Response keys**: `circuit` (`circuit_name`, `total_wattage`, `voltage_drop_pct`, `operating_voltage_at_end_v`, `is_compliant`), `recommended_transformer` (`rating_va`, `tap_v`).

### C. Master BoQ Estimate (`POST /api/v1/landscape/estimate/generate`)
```python
client.post(
    "/api/v1/landscape/estimate/generate",
    json={
        "project_id": "PRJ-001",
        "project_title": "Садиба с. Козин",
        "eur_rate": 45.0,
        "usd_rate": 41.5,
    },
)
```
- **Response keys**: `project_id`, `sections`, `summary`, `currency_summary` (`grand_total_uah`, `grand_total_eur`, `grand_total_usd`).

### D. DSTU Album SVG Export (`POST /api/v1/landscape/album/generate-svg`)
```python
client.post(
    "/api/v1/landscape/album/generate-svg",
    json={
        "sheet_type": "master_plan",  # Allowed: 'master_plan', 'dendro_plan', 'setting_out_plan', 'boq_schedule'
        "state": {
            "project_id": "PRJ-001",
            "project_title": "Садиба с. Козин",
        },
        "title_block": {
            "project_name": "Садиба в с. Козин",  # Note: project_name, NOT project_title
            "sheet_title": "Генеральний план ділянки",
            "designer_name": "Денчик",
            "scale": "1:100",
        },
    },
)
```
- **Response keys**: `content_type` (`"image/svg+xml"`), `content` (`"<svg..."`), `filename`.

---

## 4. Visual Studio Serving & Port 8000 Dual-Server Parity (`main.py` + `canvas_bridge.py`)

### A. Port 8000 Entrypoint Pitfall (`dnk_canvas.sh` vs `apps.api.main:app`)
- In local DNK OS environments, `scripts/system/dnk_canvas.sh` often holds port `8000` running `uvicorn scripts.system.canvas_bridge:app --host 127.0.0.1 --port 8000` rather than `apps.api.main:app`.
- **Rule**: Whenever mounting new visual studios or domain routers intended for `http://127.0.0.1:8000/docs`, wire them in **both** `apps/api/main.py` AND `scripts/system/canvas_bridge.py`, and restart the active `uvicorn` process on port `8000` if needed so Swagger UI (`/docs`) immediately reflects all endpoints.

### B. Route Separation (`/studio` vs `/landscape`)
- `GET /studio` is reserved in `apps/api/main.py` for the Unified DNK OS Studio (`core/canvas/dnk_studio.html`).
- **DNK Landscape Studio** (`core/landscape/studio.html`, local BloomsEye-style interactive 2D/3D planner) is served at `GET /api/v1/landscape/studio` (`HTMLResponse`) with a top-level convenience redirect at `GET /landscape` -> `/api/v1/landscape/studio`.

