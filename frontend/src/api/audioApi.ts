import { apiUpload } from './client';
import { AudioAnalysisResult } from '../types';
import { isNetworkError, mockApi } from './mockData';

export const audioApi = {
  async analyze(file: File | Blob, fileName = 'recording.webm'): Promise<AudioAnalysisResult> {
    try {
      return await apiUpload<AudioAnalysisResult>('/audio/analyze', file, fileName);
    } catch (error) {
      if (isNetworkError(error)) return mockApi.analyzeAudio();
      throw error;
    }
  },
};
