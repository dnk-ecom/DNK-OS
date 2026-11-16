# Synthetic Customer Swarm HUD & Funnel Stream Pattern (SAAP v1.0)

## Architecture Overview
The SAAP v1.0 (Synthetic Customer Swarm Engine) provides real-time simulation of customer cohorts navigating an e-commerce funnel, outputting conversion rates, drop-offs, and grounded objections. Integrating this engine directly into the Spatial Visual Canvas HUD (`@xyflow/react` / Next.js) enables operators to run what-if simulations visually on the canvas.

## Key Architectural Components

### 1. W3C SSE Stream Client (`simulation_client.ts`)
- **Transport**: Native `fetch` with `ReadableStream` reader parsing `data: <json>\n\n` SSE chunks.
- **Event Types**:
  - `step_progress`: Incremental step progression (landing -> pdp -> cart -> checkout) with per-step conversion and drop-off tallies.
  - `complete`: Final aggregated simulation summary, top objections, and recommendations.
  - `error`: Error payload and graceful stream termination.
- **Resilience**: Auto-fallback to synchronous REST simulation (`/api/v1/simulation/simulate-funnel`) if the SSE stream encounters transport failure.

### 2. Spatial Custom Node (`CustomerSwarmNode.tsx`)
- **ReactFlow Integration**: Implements `@xyflow/react` NodeProps with Handles for directional flow:
  - `in-left`: Connects from product seed / offer nodes.
  - `out-right`: Connects to downstream marketing / retargeting / copy refactor nodes.
- **Interactive Multi-Tab HUD**:
  - **Funnel HUD**: Live pulsating progress bars, step-by-step conversion counts, and drop-off percentages.
  - **Hard-No Dissent**: Evidence-grounded objections from adversarial skeptic personas to prevent Yes-Man Bias, coupled with actionable recommendations.
  - **Parameters**: Interactive tuning of cohort size, price, and dissent seats directly within the canvas node.
- **Trigger Actions**:
  - 1-Click "Run Swarm Simulation" triggering SSE streaming and real-time state hydration.

### 3. Node Registration Invariants
To ensure the custom node is recognized across the entire canvas subsystem:
1. Register in `DNKCanvas.tsx` `nodeTypes` map: `customer_swarm: CustomerSwarmNode`.
2. Register in `CanvasEngine.tsx` `nodeTypes` map: `customer_swarm: CustomerSwarmNode`.
3. Register in `app/canvas/mvr/page.tsx` `nodeTypes` map.
4. Declare node metadata in `NodeRegistry.ts` under category `'ecommerce'` with typed input/output ports.
