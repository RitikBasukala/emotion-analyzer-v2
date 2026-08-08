import { apiRequest } from './client';
import { AnalysisHistory, ModalityType } from '../types';
import { isNetworkError, mockApi } from './mockData';

export interface HistoryQuery {
  modality?: ModalityType;
  limit?: number;
  offset?: number;
}

export const historyApi = {
  async list({ modality, limit = 20, offset = 0 }: HistoryQuery = {}): Promise<AnalysisHistory> {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (modality) params.set('modality', modality);
    try {
      return await apiRequest<AnalysisHistory>(`/history?${params.toString()}`);
    } catch (error) {
      if (isNetworkError(error)) return mockApi.getHistory();
      throw error;
    }
  },
};
