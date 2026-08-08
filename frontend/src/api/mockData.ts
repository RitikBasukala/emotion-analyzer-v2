/**
 * Lightweight offline fallback used only when the real backend cannot be
 * reached (network failure), so the UI stays demoable without a running
 * API. This is intentionally not the primary code path - every `api/*`
 * module always attempts the real HTTP call first and only falls back to
 * these generators when `fetch` itself throws (e.g. connection refused).
 */
import { EMOTIONS } from '../types';
import type {
  AudioAnalysisResult,
  EmotionPrediction,
  FusionResult,
  FuseRequest,
  TextAnalysisResult,
  VideoAnalysisResult,
} from '../types';

function randomProbabilities(): Record<string, number> {
  const raw = EMOTIONS.map(() => Math.random());
  const sum = raw.reduce((a, b) => a + b, 0);
  const probs: Record<string, number> = {};
  EMOTIONS.forEach((emotion, i) => {
    probs[emotion] = raw[i] / sum;
  });
  return probs;
}

function dominant(probs: Record<string, number>): string {
  return Object.entries(probs).reduce((a, b) => (a[1] > b[1] ? a : b))[0];
}

function mockPrediction(modelName: string): EmotionPrediction {
  const probabilities = randomProbabilities();
  const emotion = dominant(probabilities);
  return {
    emotion,
    confidence: probabilities[emotion],
    probabilities,
    model_name: modelName,
    inference_time_ms: Math.round(20 + Math.random() * 150),
  };
}

function mockTiers(finalProbabilities: Record<string, number>) {
  return {
    early_fusion_vector: Array.from({ length: 16 }, () => Math.random()),
    mid_fusion_probabilities: randomProbabilities(),
    late_fusion_probabilities: finalProbabilities,
  };
}

function mockFusion(overrides: Partial<FuseRequest> = {}): FusionResult {
  const finalProbabilities = randomProbabilities();
  const finalEmotion = dominant(finalProbabilities);
  const text = overrides.text_emotion ?? null;
  const audio = overrides.audio_emotion ?? null;
  const facial = overrides.facial_emotion ?? null;

  const contribution = (pred: EmotionPrediction | null, weight: number) => ({
    weight,
    emotion: pred?.emotion ?? null,
    confidence: pred?.confidence ?? 0,
    contribution_to_final: pred ? weight * pred.confidence : 0,
    agreement: pred?.emotion === finalEmotion,
  });

  return {
    text_emotion: text,
    audio_emotion: audio,
    facial_emotion: facial,
    final_emotion: finalEmotion,
    final_confidence: finalProbabilities[finalEmotion],
    final_probabilities: finalProbabilities,
    fusion_weights: { text: 0.3, audio: 0.3, facial: 0.4 },
    fusion_method: 'weighted_soft_voting (offline demo)',
    modality_contributions: {
      text: contribution(text, 0.3),
      audio: contribution(audio, 0.3),
      facial: contribution(facial, 0.4),
    },
    tiers: mockTiers(finalProbabilities),
    inference_time_ms: Math.round(80 + Math.random() * 200),
  };
}

export const mockApi = {
  analyzeText(text: string): TextAnalysisResult {
    return {
      analysis_id: `demo-${Date.now()}`,
      modality: 'text',
      text,
      prediction: mockPrediction('demo-roberta'),
      created_at: new Date().toISOString(),
    };
  },

  analyzeAudio(): AudioAnalysisResult {
    const toneEmotion = mockPrediction('demo-wav2vec2');
    const textEmotion = mockPrediction('demo-roberta');
    return {
      analysis_id: `demo-${Date.now()}`,
      modality: 'audio',
      transcript: 'This is a simulated offline transcript of your audio.',
      tone_emotion: toneEmotion,
      text_emotion: textEmotion,
      fusion: mockFusion({ text_emotion: textEmotion, audio_emotion: toneEmotion }),
      audio_duration_seconds: 4.2,
      created_at: new Date().toISOString(),
    };
  },

  analyzeVideo(): VideoAnalysisResult {
    const facialEmotion = mockPrediction('demo-deepface');
    const frameEmotions = Array.from({ length: 10 }, (_, i) => {
      const probabilities = randomProbabilities();
      const emotion = dominant(probabilities);
      return { frame_index: i, emotion, confidence: probabilities[emotion], probabilities };
    });
    return {
      analysis_id: `demo-${Date.now()}`,
      modality: 'video',
      transcript: null,
      facial_emotion: facialEmotion,
      audio_emotion: null,
      text_emotion: null,
      fusion: mockFusion({ facial_emotion: facialEmotion }),
      frame_count: frameEmotions.length,
      frame_emotions: frameEmotions,
      audio_duration_seconds: null,
      created_at: new Date().toISOString(),
    };
  },

  fuse(payload: FuseRequest): FusionResult {
    return mockFusion(payload);
  },

  getHistory() {
    return { items: [], total: 0 };
  },
};

/** True only for low-level network failures, not HTTP error responses. */
export function isNetworkError(error: unknown): boolean {
  return error instanceof TypeError;
}
