// Owner: Person 3
// Purpose: TypeScript types matching backend FastAPI Pydantic schemas

export interface HealthResponse {
  status: string;
  app: string;
  provider: string;
}

export interface ActivityLogItem {
  id: string;
  action_type: string;
  params: Record<string, any>;
  agent: string;
  provider: string;
  status: string;
  undo_payload?: Record<string, any> | null;
  created_at?: string;
}

export interface ActivityListResponse {
  activities: ActivityLogItem[];
  total: number;
}

export interface UndoResponse {
  success: boolean;
  action_id: string;
  message: string;
}

export interface ApprovalItem {
  id: string;
  action_type: string;
  params: Record<string, any>;
  agent: string;
  provider: string;
  prompt: string;
  status: string;
  created_at?: string;
}

export interface ApprovalsListResponse {
  approvals: ApprovalItem[];
  total: number;
}

export interface ApprovalDecisionResponse {
  id: string;
  status: string;
  message: string;
}

export interface PermissionsMapResponse {
  permissions: Record<string, string>;
}

export interface SettingsResponse {
  provider: string;
  offline_mode: boolean;
  byo_api_key_enabled: boolean;
  telemetry: boolean;
  nebius_base_url: string;
  ollama_host: string;
}

export interface ResetSeedResponse {
  status: string;
  message: string;
  seeded_items: number;
}

export interface AgentRunResponse {
  agent: string;
  provider: string;
  status: string;
  output: any;
}
