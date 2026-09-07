import { useAuthStore } from '../store/authStore';
import { useWorkspaceStore } from '../store/workspaceStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export class APIError extends Error {
  status: number;
  data: any;

  constructor(status: number, data: any) {
    let message = `API Error: ${status}`;
    
    if (status === 422 && Array.isArray(data?.detail)) {
      const firstError = data.detail[0];
      const fieldPath = firstError.loc?.filter((p: string | number) => p !== 'body').join('.') || 'Field';
      message = `Validation Error: ${fieldPath} - ${firstError.msg}`;
    } else if (data?.detail && typeof data.detail === 'string') {
      message = data.detail;
    }

    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = new Headers(options.headers);
  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const { token, logout } = useAuthStore.getState();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      logout();
    }
    let errorData;
    try {
      errorData = await response.json();
    } catch {
      errorData = { detail: response.statusText };
    }
    
    if (response.status === 404 && errorData?.detail === "Workspace not found or access denied") {
      useWorkspaceStore.getState().clearActiveWorkspace();
      window.location.reload();
    }
    
    throw new APIError(response.status, errorData);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const apiClient = {
  get: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'GET' }),
  post: <T>(endpoint: string, body: any, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'POST', body: body instanceof FormData ? body : JSON.stringify(body) }),
  put: <T>(endpoint: string, body: any, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'PUT', body: body instanceof FormData ? body : JSON.stringify(body) }),
  patch: <T>(endpoint: string, body: any, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'PATCH', body: body instanceof FormData ? body : JSON.stringify(body) }),
  delete: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'DELETE' }),
};
