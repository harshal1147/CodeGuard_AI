const API_URL = '';
const TOKEN_KEY = 'codeguard_token';
export const AUTH_CHANGE_EVENT = 'codeguard-auth-change';

function notifyAuthChange(): void {
  if (typeof window !== 'undefined') window.dispatchEvent(new Event(AUTH_CHANGE_EVENT));
}

export type ApiEnvelope<T> = {
  success: boolean;
  data: T;
};

export type CurrentUser = {
  id: string;
  name: string;
  email: string;
};

export type Project = {
  id: string;
  name: string;
  description: string | null;
};

export type AnalysisIssue = {
  type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  title: string;
  message: string;
  line: number | null;
  recommendation: string;
  category: string;
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
};

export type AnalysisMetrics = {
  cyclomatic_complexity: number | null;
  cyclomatic_rating: string;
  estimated_time_complexity: string;
  estimated_space_complexity: string;
  complexity_is_estimate: boolean;
  quality_scores: Record<string, number>;
};

export type AnalysisReport = {
  id: string;
  project_id: string;
  language: string;
  status: string;
  score: number | null;
  findings_count: number;
  result: {
    filename: string;
    issues: AnalysisIssue[];
    metrics: AnalysisMetrics;
    severity_counts: Record<string, number>;
  };
};

export type AnalysisHistoryItem = {
  id: string;
  project_id: string;
  project_name: string;
  filename: string;
  language: string;
  status: string;
  score: number | null;
  findings_count: number;
  created_at: string;
  severity_counts: Record<string, number>;
};

export type AnalysisDetails = Omit<AnalysisReport, 'result'> & {
  result: AnalysisReport['result'] | null;
  created_at: string;
};

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  const payload: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    if (response.status === 401 && token) clearStoredToken();
    const body = payload as { detail?: unknown; error?: { message?: string } } | null;
    const message = typeof body?.detail === 'string'
      ? body.detail
      : body?.error?.message ?? `Request failed (${response.status}).`;
    throw new Error(message);
  }
  return payload as T;
}

export function getStoredToken(): string | null {
  if (typeof window === 'undefined') return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function clearStoredToken(): void {
  if (typeof window === 'undefined') return;
  window.localStorage.removeItem(TOKEN_KEY);
  notifyAuthChange();
}

export async function authenticate(
  endpoint: 'login' | 'register',
  values: { name?: string; email: string; password: string },
): Promise<CurrentUser> {
  const response = await request<ApiEnvelope<{ user: CurrentUser; token: string }>>(
    `/api/auth/${endpoint}`,
    { method: 'POST', body: JSON.stringify(values) },
  );
  window.localStorage.setItem(TOKEN_KEY, response.data.token);
  notifyAuthChange();
  return response.data.user;
}

export async function getOrCreateProject(token: string): Promise<Project> {
  const existing = await request<ApiEnvelope<Project[]>>('/api/projects', {}, token);
  if (existing.data.length > 0) return existing.data[0];

  const created = await request<ApiEnvelope<Project>>(
    '/api/projects',
    {
      method: 'POST',
      body: JSON.stringify({ name: 'Code Review', description: 'CodeGuard AI analysis project' }),
    },
    token,
  );
  return created.data;
}

export async function submitAnalysis(
  token: string,
  values: { project_id: string; language: string; filename: string; code: string },
): Promise<AnalysisReport> {
  const response = await request<ApiEnvelope<AnalysisReport>>(
    '/api/analysis',
    { method: 'POST', body: JSON.stringify({ ...values, source: 'editor' }) },
    token,
  );
  return response.data;
}

export async function getAnalysisHistory(token: string): Promise<AnalysisHistoryItem[]> {
  const response = await request<ApiEnvelope<AnalysisHistoryItem[]>>('/api/analysis/history', {}, token);
  return response.data;
}

export async function getAnalysis(token: string, analysisId: string): Promise<AnalysisDetails> {
  const response = await request<ApiEnvelope<AnalysisDetails>>(
    `/api/analysis/${encodeURIComponent(analysisId)}`,
    {},
    token,
  );
  return response.data;
}
