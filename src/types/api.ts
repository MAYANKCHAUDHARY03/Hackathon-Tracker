export interface HealthResponse {
  status: string;
  environment: string;
  api_version: string;
  database: string;
}

export interface ApiErrorResponse {
  detail: string;
}

// Wrap responses that use pagination or lists
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}
