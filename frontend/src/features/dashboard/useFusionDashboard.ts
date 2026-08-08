import { useEffect, useMemo, useState } from 'react';
import { fusionApi } from '../../api';
import { FusionResult } from '../../types';
import { useLastResults } from '../../hooks/useLastResults';

export function useFusionDashboard() {
  const { lastText, lastAudio, lastVideo, bestTextEmotion, bestAudioEmotion, bestFacialEmotion } = useLastResults();

  const [includeText, setIncludeText] = useState(true);
  const [includeAudio, setIncludeAudio] = useState(true);
  const [includeFacial, setIncludeFacial] = useState(true);

  const [fusion, setFusion] = useState<FusionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const payload = useMemo(() => ({
    text_emotion: includeText && bestTextEmotion ? bestTextEmotion : undefined,
    audio_emotion: includeAudio && bestAudioEmotion ? bestAudioEmotion : undefined,
    facial_emotion: includeFacial && bestFacialEmotion ? bestFacialEmotion : undefined,
  }), [includeText, includeAudio, includeFacial, bestTextEmotion, bestAudioEmotion, bestFacialEmotion]);

  const hasAnySignal = Boolean(payload.text_emotion || payload.audio_emotion || payload.facial_emotion);

  useEffect(() => {
    if (!hasAnySignal) {
      setFusion(null);
      return;
    }

    let cancelled = false;
    setLoading(true);
    setError(null);

    fusionApi
      .fuse(payload)
      .then((result) => {
        if (!cancelled) setFusion(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to fuse modalities');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [payload, hasAnySignal]);

  return {
    lastText,
    lastAudio,
    lastVideo,
    includeText,
    includeAudio,
    includeFacial,
    setIncludeText,
    setIncludeAudio,
    setIncludeFacial,
    hasTextSignal: Boolean(bestTextEmotion),
    hasAudioSignal: Boolean(bestAudioEmotion),
    hasFacialSignal: Boolean(bestFacialEmotion),
    fusion,
    loading,
    error,
    hasAnySignal,
  };
}
