/**
 * Thin, fully typed HTTP client for the emotion-recognition backend.
 * No authentication is involved anywhere - the backend is fully open.
 */

export const API_URL =
  (import.meta.env.VITE_API_URL as string | undefined) || 'http://localhost:8000/api/v1';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function parseErrorMessage(response: Response): Promise<string> {
  try {
    const data = await response.json();
    return data?.detail || data?.message || `Request failed with status ${response.status}`;
  } catch {
    return `Request failed with status ${response.status}`;
  }
}

export async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    throw new ApiError(await parseErrorMessage(response), response.status);
  }

  return response.json() as Promise<T>;
}

export async function apiUpload<T>(endpoint: string, file: File | Blob, fileName?: string): Promise<T> {
  const formData = new FormData();
  formData.append('file', file, fileName);

  const response = await fetch(`${API_URL}${endpoint}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new ApiError(await parseErrorMessage(response), response.status);
  }

  return response.json() as Promise<T>;
}
