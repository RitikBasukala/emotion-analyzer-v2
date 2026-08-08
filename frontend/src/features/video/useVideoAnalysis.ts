import { useState } from 'react';
import { videoApi } from '../../api';
import { VideoAnalysisResult } from '../../types';
import { useLastResults } from '../../hooks/useLastResults';

export function useVideoAnalysis() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<VideoAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { setLastVideo } = useLastResults();

  function selectFile(nextFile: File) {
    setFile(nextFile);
    setResult(null);
    setError(null);
  }

  function clearFile() {
    setFile(null);
    setResult(null);
    setError(null);
  }

  async function analyze() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const data = await videoApi.analyze(file, file.name);
      setResult(data);
      setLastVideo(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze video');
    } finally {
      setLoading(false);
    }
  }

  return { file, loading, result, error, selectFile, clearFile, analyze };
}
