import { apiRequest } from './client';
import { TextAnalysisResult } from '../types';
import { isNetworkError, mockApi } from './mockData';

export const textApi = {
  async analyze(text: string): Promise<TextAnalysisResult> {
    try {
      return await apiRequest<TextAnalysisResult>('/text/analyze', {
        method: 'POST',
        body: JSON.stringify({ text }),
      });
    } catch (error) {
      if (isNetworkError(error)) return mockApi.analyzeText(text);
      throw error;
    }
  },
};
