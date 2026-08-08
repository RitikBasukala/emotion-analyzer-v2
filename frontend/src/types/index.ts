export type EmotionType =
  | 'Happy'
  | 'Sad'
  | 'Angry'
  | 'Fear'
  | 'Surprise'
  | 'Disgust'
  | 'Neutral';

export type ModalityType = 'text' | 'audio' | 'video';

export interface EmotionPrediction {
  emotion: string;
  confidence: number;
  probabilities: Record<string, number>;
  model_name?: string;
  inference_time_ms?: number;
}

export interface ModalityContribution {
  weight: number;
  emotion: string | null;
  confidence: number;
  contribution_to_final: number;
  agreement: boolean;
}

export interface FusionTiers {
  early_fusion_vector: number[];
  mid_fusion_probabilities: Record<string, number>;
  late_fusion_probabilities: Record<string, number>;
}

export interface FusionResult {
  text_emotion: EmotionPrediction | null;
  audio_emotion: EmotionPrediction | null;
  facial_emotion: EmotionPrediction | null;
  final_emotion: string;
  final_confidence: number;
  final_probabilities: Record<string, number>;
  fusion_weights: { text: number; audio: number; facial: number };
  fusion_method: string;
  modality_contributions: Record<string, ModalityContribution>;
  tiers: FusionTiers;
  inference_time_ms: number;
}

export interface TextAnalysisResult {
  analysis_id: string;
  modality: 'text';
  text: string;
  prediction: EmotionPrediction;
  created_at: string;
}

export interface AudioAnalysisResult {
  analysis_id: string;
  modality: 'audio';
  transcript: string | null;
  tone_emotion: EmotionPrediction;
  text_emotion: EmotionPrediction | null;
  fusion: FusionResult;
  audio_duration_seconds: number | null;
  created_at: string;
}

export interface FrameEmotion {
  frame_index: number;
  emotion: string;
  confidence: number;
  probabilities: Record<string, number>;
}

export interface VideoAnalysisResult {
  analysis_id: string;
  modality: 'video';
  transcript: string | null;
  facial_emotion: EmotionPrediction;
  audio_emotion: EmotionPrediction | null;
  text_emotion: EmotionPrediction | null;
  fusion: FusionResult;
  frame_count: number | null;
  frame_emotions: FrameEmotion[] | null;
  audio_duration_seconds: number | null;
  created_at: string;
}

export interface FuseRequest {
  text_emotion?: EmotionPrediction;
  audio_emotion?: EmotionPrediction;
  facial_emotion?: EmotionPrediction;
}

export interface AnalysisHistoryItem {
  id: string;
  modality: ModalityType;
  final_emotion: string;
  confidence: number;
  created_at: string;
  input_preview?: string;
}

export interface AnalysisHistory {
  items: AnalysisHistoryItem[];
  total: number;
}

export const EMOTIONS: EmotionType[] = [
  'Happy',
  'Sad',
  'Angry',
  'Fear',
  'Surprise',
  'Disgust',
  'Neutral',
];

/**
 * Semantic emotion-tag colors. Intentionally distinct from the brand
 * palette (violet/rose/zinc) so emotion tags remain visually
 * unambiguous wherever they appear alongside brand-colored UI.
 */
export const EMOTION_COLORS: Record<EmotionType, string> = {
  Happy: '#facc15',
  Sad: '#38bdf8',
  Angry: '#fb2c36',
  Fear: '#a855f7',
  Surprise: '#fb923c',
  Disgust: '#4ade80',
  Neutral: '#94a3b8',
};

export const EMOTION_ICONS: Record<EmotionType, string> = {
  Happy: '😊',
  Sad: '😢',
  Angry: '😠',
  Fear: '😨',
  Surprise: '😲',
  Disgust: '🤢',
  Neutral: '😐',
};
