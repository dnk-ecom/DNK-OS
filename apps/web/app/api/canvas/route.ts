// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/app/api/canvas/route.ts"
// purpose: "Next.js Route Handler for reading and saving JSON Canvas 1.0 (.canvas) files between apps/web and docs/diagrams/"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-10-27"
// author: "Denchik Prime & DNK-e.com Maksym"
// --- END DNK-MRH-HEADER ---

import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs/promises';
import fsSync from 'fs';
import path from 'path';
import { reactFlowToJSONCanvas } from '../../../src/canvas/json-canvas/converter';
import type { JSONCanvasDocument } from '../../../src/canvas/json-canvas/types';

/**
 * Locate repository root across Next.js dev/build cwd environments.
 */
function resolveHubRoot(): string {
  const candidates = [
    path.resolve(process.cwd(), '../..'),
    path.resolve(process.cwd(), '..'),
    process.cwd(),
  ];
  for (const candidate of candidates) {
    if (
      fsSync.existsSync(path.join(candidate, 'docs/canvas/projects/dnk_ecom/main.canvas')) &&
      fsSync.existsSync(path.join(candidate, 'pnpm-workspace.yaml'))
    ) {
      return candidate;
    }
  }
  for (const candidate of candidates) {
    if (fsSync.existsSync(path.join(candidate, 'docs/canvas/projects/dnk_ecom/main.canvas'))) {
      return candidate;
    }
  }
  return path.resolve(process.cwd(), '../..');
}

/**
 * Safely resolve a canvas file path within docs/ preventing directory traversal.
 */
function resolveSafeCanvasPath(fileNameOrPath?: string | null): { absolutePath: string; relativePath: string } {
  const hubRoot = resolveHubRoot();
  const raw = (fileNameOrPath || 'docs/canvas/projects/dnk_ecom/main.canvas').trim();

  // Guard against path traversal
  if (raw.includes('..') || raw.startsWith('/') || raw.startsWith('\\')) {
    throw new Error(`Invalid or forbidden path: '${raw}'`);
  }

  const clean = raw.replace(/^(\.\/)?/, '');
  const fileName = clean.endsWith('.canvas') ? clean : `${clean}.canvas`;

  // 1. Direct path within docs/
  if (fileName.startsWith('docs/')) {
    const abs = path.join(hubRoot, fileName);
    return { absolutePath: abs, relativePath: fileName };
  }

  // 2. Candidate lookups
  const candidateSubdirs = [
    'docs/canvas/projects/dnk_ecom',
    'docs/canvas/projects',
    'docs/canvas',
    'docs/diagrams',
    'docs/architecture/diagrams',
  ];

  for (const sub of candidateSubdirs) {
    const testAbs = path.join(hubRoot, sub, fileName);
    if (fsSync.existsSync(testAbs)) {
      return { absolutePath: testAbs, relativePath: `${sub}/${fileName}` };
    }
  }

  // Fallback to docs/canvas/projects/dnk_ecom
  const fallbackAbs = path.join(hubRoot, 'docs/canvas/projects/dnk_ecom', fileName);
  return { absolutePath: fallbackAbs, relativePath: `docs/canvas/projects/dnk_ecom/${fileName}` };
}

/**
 * Recursively find .canvas files in a directory.
 */
function findCanvasesRecursively(dir: string, baseRel: string): string[] {
  let list: string[] = [];
  if (!fsSync.existsSync(dir)) return list;
  try {
    const entries = fsSync.readdirSync(dir, { withFileTypes: true });
    for (const e of entries) {
      const relPath = baseRel ? `${baseRel}/${e.name}` : e.name;
      const absPath = path.join(dir, e.name);
      if (e.isDirectory() && !e.name.startsWith('.')) {
        list = list.concat(findCanvasesRecursively(absPath, relPath));
      } else if (e.isFile() && e.name.endsWith('.canvas')) {
        list.push(relPath);
      }
    }
  } catch (err) {
    console.error('[API Canvas] Error reading directory:', dir, err);
  }
  return list;
}

/**
 * List available .canvas files across docs/canvas and docs/diagrams.
 */
async function listAvailableCanvasFiles(): Promise<string[]> {
  const hubRoot = resolveHubRoot();
  const found = new Set<string>();

  const searchDirs = [
    { abs: path.join(hubRoot, 'docs/canvas'), rel: 'docs/canvas' },
    { abs: path.join(hubRoot, 'docs/architecture/diagrams'), rel: 'docs/architecture/diagrams' },
    { abs: path.join(hubRoot, 'docs/diagrams'), rel: 'docs/diagrams' },
  ];

  for (const d of searchDirs) {
    const files = findCanvasesRecursively(d.abs, d.rel);
    for (const f of files) {
      found.add(f);
    }
  }

  // Prioritize flagship project canvas
  const flagship = 'docs/canvas/projects/dnk_ecom/main.canvas';
  const pipeline = 'docs/canvas/shopify_vibe_pipeline.canvas';

  const ordered: string[] = [];
  if (found.has(flagship)) {
    ordered.push(flagship);
    found.delete(flagship);
  }
  if (found.has(pipeline)) {
    ordered.push(pipeline);
    found.delete(pipeline);
  }

  const rest = Array.from(found).sort();
  return [...ordered, ...rest];
}

/**
 * GET: Retrieve .canvas JSON Canvas 1.0 file or list available canvas files
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action');
    const fileParam = searchParams.get('file');

    const availableFiles = await listAvailableCanvasFiles();

    if (action === 'list') {
      return NextResponse.json({
        status: 'success',
        files: availableFiles,
      });
    }

    const { absolutePath, relativePath } = resolveSafeCanvasPath(fileParam);

    if (!fsSync.existsSync(absolutePath)) {
      // If file does not exist, return initial empty JSON Canvas 1.0 structure
      const emptyDoc: JSONCanvasDocument = { nodes: [], edges: [] };
      return NextResponse.json({
        status: 'not_found',
        file: relativePath,
        canvas: emptyDoc,
        files: availableFiles,
      }, { status: 404 });
    }

    const fileContent = await fs.readFile(absolutePath, 'utf-8');
    const canvasDoc = JSON.parse(fileContent);

    return NextResponse.json({
      status: 'success',
      file: relativePath,
      canvas: canvasDoc,
      files: availableFiles,
    });
  } catch (err: any) {
    return NextResponse.json(
      { status: 'error', error: err.message || 'Failed to read canvas file' },
      { status: 400 }
    );
  }
}

/**
 * POST: Save JSON Canvas 1.0 (.canvas) document or ReactFlow state to disk
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { file, canvas, nodes, edges } = body;

    const { absolutePath, relativePath } = resolveSafeCanvasPath(file);

    let docToSave: JSONCanvasDocument;

    if (canvas && Array.isArray(canvas.nodes) && Array.isArray(canvas.edges)) {
      docToSave = canvas;
    } else if (Array.isArray(nodes) && Array.isArray(edges)) {
      docToSave = reactFlowToJSONCanvas(nodes, edges);
    } else {
      return NextResponse.json(
        { status: 'error', error: 'Missing valid canvas document or nodes/edges arrays' },
        { status: 400 }
      );
    }

    // Ensure target directory exists
    const dirName = path.dirname(absolutePath);
    if (!fsSync.existsSync(dirName)) {
      await fs.mkdir(dirName, { recursive: true });
    }

    // Write formatted JSON Canvas 1.0
    await fs.writeFile(absolutePath, JSON.stringify(docToSave, null, 2), 'utf-8');

    const availableFiles = await listAvailableCanvasFiles();

    return NextResponse.json({
      status: 'success',
      file: relativePath,
      node_count: docToSave.nodes.length,
      edge_count: docToSave.edges.length,
      updated_at: new Date().toISOString(),
      files: availableFiles,
    });
  } catch (err: any) {
    return NextResponse.json(
      { status: 'error', error: err.message || 'Failed to save canvas file' },
      { status: 400 }
    );
  }
}
