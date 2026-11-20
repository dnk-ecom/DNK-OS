/*
# --- DNK-MRH-HEADER ---
# mrh_id: "packages/video-audit-core/src/pipeline/domain/artifacts/artifact.ts"
# purpose: "Canonical Versioned ArtifactManifest and Deterministic Storage Key Generators."
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-09-02"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---
*/

import { z } from 'zod';
import { AuditJobType, AuditJobTypeSchema } from '../jobs/job.js';

export const ArtifactManifestSchema = z.object({
  key: z.string().min(1),
  referenceAssetId: z.string().min(1),
  jobId: z.string().optional(),
  jobType: AuditJobTypeSchema.optional(),
  sha256: z.string().min(1),
  byteSize: z.number().int().nonnegative(),
  mimeType: z.string().min(1),
  schemaVersion: z.literal('artifact-manifest.v1'),
  createdAt: z.string().datetime(),
  metadata: z.record(z.unknown()).optional()
});

export type ArtifactManifest = z.infer<typeof ArtifactManifestSchema>;

export interface ArtifactInput {
  key: string;
  referenceAssetId: string;
  data: Buffer | Uint8Array | string;
  mimeType: string;
  jobId?: string;
  jobType?: z.infer<typeof AuditJobTypeSchema>;
  createdAt?: string;
  metadata?: Record<string, unknown>;
}

export const ArtifactKeyGenerators = {
  source(referenceAssetId: string, sha256: string, extension = 'mp4'): string {
    const ext = extension.replace(/^\./, '');
    return `references/${referenceAssetId}/source/${sha256}.${ext}`;
  },
  transcription(referenceAssetId: string, processorVersion: string): string {
    return `references/${referenceAssetId}/transcript/${processorVersion}.json`;
  },
  scene_extraction(referenceAssetId: string, processorVersion: string): string {
    return `references/${referenceAssetId}/scenes/${processorVersion}.json`;
  },
  ocr(referenceAssetId: string, processorVersion: string): string {
    return `references/${referenceAssetId}/ocr/${processorVersion}.json`;
  },
  audio_analysis(referenceAssetId: string, processorVersion: string): string {
    return `references/${referenceAssetId}/audio/${processorVersion}.json`;
  },
  multimodal_audit(referenceAssetId: string, modelSetVersion: string): string {
    return `references/${referenceAssetId}/audit/${modelSetVersion}.json`;
  },
  report_assembly(referenceAssetId: string, reportVersion: string): string {
    return `references/${referenceAssetId}/report/${reportVersion}.json`;
  },
  adaptation(referenceAssetId: string, adaptationId: string): string {
    return `references/${referenceAssetId}/adaptation/${adaptationId}.json`;
  }
};

export function generateDeterministicArtifactKey(
  type: AuditJobType,
  referenceAssetId: string,
  versionOrSha: string
): string {
  if (type === 'ingestion') {
    return ArtifactKeyGenerators.source(referenceAssetId, versionOrSha);
  }
  const generator = (ArtifactKeyGenerators as any)[type];
  if (typeof generator === 'function') {
    return generator(referenceAssetId, versionOrSha);
  }
  return `references/${referenceAssetId}/${type}/${versionOrSha}.json`;
}
