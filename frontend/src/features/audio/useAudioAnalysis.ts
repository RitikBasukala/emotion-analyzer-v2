import { useState } from 'react';
import { audioApi } from '../../api';
import { AudioAnalysisResult } from '../../types';
import { useLastResults } from '../../hooks/useLastResults';

export function useAudioAnalysis() {
  const [file, setFile] = useState<File | Blob | null>(null);
  const [fileName, setFileName] = useState<string>('recording.webm');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AudioAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { setLastAudio } = useLastResults();

  function selectFile(nextFile: File | Blob, name?: string) {
    setFile(nextFile);
    setFileName(name ?? (nextFile instanceof File ? nextFile.name : 'recording.webm'));
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
      const data = await audioApi.analyze(file, fileName);
      setResult(data);
      setLastAudio(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze audio');
    } finally {
      setLoading(false);
    }
  }

  return { file, fileName, loading, result, error, selectFile, clearFile, analyze };
}
