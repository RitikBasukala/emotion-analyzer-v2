import { useState } from 'react';
import { textApi } from '../../api';
import { TextAnalysisResult } from '../../types';
import { useLastResults } from '../../hooks/useLastResults';

export function useTextAnalysis() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TextAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { setLastText } = useLastResults();

  async function analyze() {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await textApi.analyze(text);
      setResult(data);
      setLastText(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze text');
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setText('');
    setResult(null);
    setError(null);
  }

  return { text, setText, loading, result, error, analyze, reset };
}
