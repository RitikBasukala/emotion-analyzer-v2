import { useCallback, useEffect, useState } from 'react';
import { historyApi } from '../api';
import { AnalysisHistoryItem, ModalityType } from '../types';

interface UseAnalysisHistoryOptions {
  modality?: ModalityType | 'all';
  limit?: number;
}

export function useAnalysisHistory({ modality = 'all', limit = 10 }: UseAnalysisHistoryOptions = {}) {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await historyApi.list({
        modality: modality === 'all' ? undefined : modality,
        limit,
        offset,
      });
      setItems(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load history');
    } finally {
      setLoading(false);
    }
  }, [modality, limit, offset]);

  useEffect(() => {
    load();
  }, [load]);

  return {
    items,
    total,
    loading,
    error,
    offset,
    limit,
    setOffset,
    reload: load,
    page: Math.floor(offset / limit) + 1,
    totalPages: Math.max(1, Math.ceil(total / limit)),
  };
}
