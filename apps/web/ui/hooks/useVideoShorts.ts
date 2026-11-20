// --- DNK-MRH-HEADER ---
// mrh_id: "apps/web/ui/hooks/useVideoShorts.ts"
// purpose: "React hook for OpenMontage Shorts extraction, kinetic preview, and Remotion composition"
// canonical_source: true
// alters_files: []
// triggers_tasks: []
// status: "Active"
// version: "1.0.0"
// updated_at: "2026-09-14"
// author: "DNK Swarm (dnk_dev_fullstack & gerych_builder)"
// --- END DNK-MRH-HEADER ---

import { useState } from 'react';
import { apiClient } from '../lib/api';

export interface WordTimestamp {
  word: string;
  start: number;
  end: number;
  score?: number;
}

export interface TimeRange {
  start: number;
  end: number;
  duration: number;
}

export interface DisfluencyItem {
  word: string;
  start: number;
  end: number;
}

export interface HighlightCandidate {
  id: string;
  start_time: number;
  end_time: number;
  duration: number;
  transcript: string;
  retention_score: number;
  hook_strength: number;
  speech_rate_wpm: number;
  words: WordTimestamp[];
  cut_pauses: TimeRange[];
}

export interface ExtractHighlightsResponse {
  source_id: string;
  total_candidates: number;
  candidates: HighlightCandidate[];
  detected_silences: TimeRange[];
  filtered_disfluencies: DisfluencyItem[];
  video_receipt: Record<string, any>;
}

export interface ComposeShortResponse {
  status: string;
  title: string;
  composition: {
    composition_id: string;
    width: number;
    height: number;
    fps: number;
    duration_in_frames: number;
    default_props: Record<string, any>;
  };
  video_receipt: Record<string, any>;
}

export interface ExportEdlResponse {
  format: string;
  source_media: string;
  clips_count: number;
  events: Array<Record<string, any>>;
}

export function useVideoShorts() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [highlightData, setHighlightData] = useState<ExtractHighlightsResponse | null>(null);
  const [composedData, setComposedData] = useState<ComposeShortResponse | null>(null);

  const extractHighlights = async (
    words: WordTimestamp[],
    sourceId = 'source_stream',
    topK = 5
  ): Promise<ExtractHighlightsResponse> => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.post<ExtractHighlightsResponse>(
        '/api/v1/video/shorts/extract-highlights',
        {
          words,
          source_id: sourceId,
          top_k: topK,
        }
      );
      setHighlightData(res);
      return res;
    } catch (err: any) {
      console.error('Error extracting highlights:', err);
      setError(err?.message || 'Failed to extract video highlights');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const composeShort = async (
    params: {
      candidate?: HighlightCandidate;
      words?: WordTimestamp[];
      mediaSrc?: string;
      username?: string;
      title?: string;
      accentColor?: string;
    }
  ): Promise<ComposeShortResponse> => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.post<ComposeShortResponse>(
        '/api/v1/video/shorts/compose',
        {
          candidate: params.candidate,
          words: params.words,
          media_src: params.mediaSrc || 'https://assets.dnk-e.com/raw_source.mp4',
          username: params.username || '@dnk_os',
          title: params.title,
          accent_color: params.accentColor || '#06B6D4',
          include_progress_bar: true,
          include_badge: true,
        }
      );
      setComposedData(res);
      return res;
    } catch (err: any) {
      console.error('Error composing short:', err);
      setError(err?.message || 'Failed to compose short video');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const exportEdl = async (
    sourceMedia: string,
    candidates?: HighlightCandidate[],
    words?: WordTimestamp[]
  ): Promise<ExportEdlResponse> => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.post<ExportEdlResponse>(
        '/api/v1/video/shorts/export-edl',
        {
          source_media: sourceMedia,
          candidates,
          words,
        }
      );
      return res;
    } catch (err: any) {
      console.error('Error exporting EDL:', err);
      setError(err?.message || 'Failed to export EDL');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    error,
    highlightData,
    composedData,
    extractHighlights,
    composeShort,
    exportEdl,
  };
}
