import { apiRequest } from './client';
import { FusionResult, FuseRequest } from '../types';
import { isNetworkError, mockApi } from './mockData';

export const fusionApi = {
  async fuse(payload: FuseRequest): Promise<FusionResult> {
    try {
      return await apiRequest<FusionResult>('/fuse', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
    } catch (error) {
      if (isNetworkError(error)) return mockApi.fuse(payload);
      throw error;
    }
  },
};
