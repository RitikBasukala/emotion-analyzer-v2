import { apiUpload } from './client';
import { VideoAnalysisResult } from '../types';
import { isNetworkError, mockApi } from './mockData';

export const videoApi = {
  async analyze(file: File | Blob, fileName = 'clip.webm'): Promise<VideoAnalysisResult> {
    try {
      return await apiUpload<VideoAnalysisResult>('/video/analyze', file, fileName);
    } catch (error) {
      if (isNetworkError(error)) return mockApi.analyzeVideo();
      throw error;
    }
  },
};
