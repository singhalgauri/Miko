// Owner: Person 3
// Purpose: Typed REST client for Miko backend API

import {
  ActivityListResponse,
  AgentRunResponse,
  ApprovalDecisionResponse,
  ApprovalsListResponse,
  HealthResponse,
  PermissionsMapResponse,
  ResetSeedResponse,
  SettingsResponse,
  UndoResponse,
} from './types';

const API_BASE = '';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`API Error ${res.status}: ${errorText || res.statusText}`);
  }
  return res.json();
}

export const api = {
  getHealth: (): Promise<HealthResponse> => fetchJson('/health'),

  getActivity: (limit = 50): Promise<ActivityListResponse> =>
    fetchJson(`/api/activity?limit=${limit}`),

  undoAction: (actionId: string): Promise<UndoResponse> =>
    fetchJson('/api/activity/undo', {
      method: 'POST',
      body: JSON.stringify({ action_id: actionId }),
    }),

  getApprovals: (): Promise<ApprovalsListResponse> => fetchJson('/api/approvals'),

  decideApproval: (id: string, approved: boolean): Promise<ApprovalDecisionResponse> =>
    fetchJson(`/api/approvals/${id}/decide`, {
      method: 'POST',
      body: JSON.stringify({ approved }),
    }),

  getPermissions: (): Promise<PermissionsMapResponse> => fetchJson('/api/permissions'),

  updatePermission: (actionType: string, policy: string): Promise<{ success: boolean }> =>
    fetchJson('/api/permissions', {
      method: 'POST',
      body: JSON.stringify({ action_type: actionType, policy }),
    }),

  getSettings: (): Promise<SettingsResponse> => fetchJson('/api/settings'),

  updateSettings: (newSettings: Partial<SettingsResponse>): Promise<SettingsResponse> =>
    fetchJson('/api/settings', {
      method: 'POST',
      body: JSON.stringify(newSettings),
    }),

  resetSeedData: (): Promise<ResetSeedResponse> =>
    fetchJson('/api/seed/reset', { method: 'POST' }),

  runAgent: (name: string, inputText = '', parameters = {}): Promise<AgentRunResponse> =>
    fetchJson(`/api/agents/${name}/run`, {
      method: 'POST',
      body: JSON.stringify({ input_text: inputText, parameters }),
    }),
};
