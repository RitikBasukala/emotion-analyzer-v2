import { createContext, useContext, useMemo, useState, ReactNode } from 'react';
import { AudioAnalysisResult, EmotionPrediction, TextAnalysisResult, VideoAnalysisResult } from '../types';

interface LastResultsState {
  lastText: TextAnalysisResult | null;
  lastAudio: AudioAnalysisResult | null;
  lastVideo: VideoAnalysisResult | null;
  setLastText: (result: TextAnalysisResult | null) => void;
  setLastAudio: (result: AudioAnalysisResult | null) => void;
  setLastVideo: (result: VideoAnalysisResult | null) => void;
  /** Best-known text-emotion signal, preferring the standalone text page. */
  bestTextEmotion: EmotionPrediction | null;
  /** Best-known acoustic/tone emotion signal, from audio or video's audio track. */
  bestAudioEmotion: EmotionPrediction | null;
  /** Best-known facial emotion signal, from the video pipeline. */
  bestFacialEmotion: EmotionPrediction | null;
}

const LastResultsContext = createContext<LastResultsState | null>(null);

export function LastResultsProvider({ children }: { children: ReactNode }) {
  const [lastText, setLastText] = useState<TextAnalysisResult | null>(null);
  const [lastAudio, setLastAudio] = useState<AudioAnalysisResult | null>(null);
  const [lastVideo, setLastVideo] = useState<VideoAnalysisResult | null>(null);

  const value = useMemo<LastResultsState>(() => ({
    lastText,
    lastAudio,
    lastVideo,
    setLastText,
    setLastAudio,
    setLastVideo,
    bestTextEmotion: lastText?.prediction ?? lastAudio?.text_emotion ?? lastVideo?.text_emotion ?? null,
    bestAudioEmotion: lastAudio?.tone_emotion ?? lastVideo?.audio_emotion ?? null,
    bestFacialEmotion: lastVideo?.facial_emotion ?? null,
  }), [lastText, lastAudio, lastVideo]);

  return <LastResultsContext.Provider value={value}>{children}</LastResultsContext.Provider>;
}

export function useLastResults() {
  const context = useContext(LastResultsContext);
  if (!context) {
    throw new Error('useLastResults must be used within a LastResultsProvider');
  }
  return context;
}
