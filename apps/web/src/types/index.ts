export interface User {
  id: string
  email: string
  full_name: string
  phone?: string
  is_active: boolean
  is_superuser: boolean
  department_id?: string
  created_at: string
  last_login_at?: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export type CameraStatus = 'online' | 'offline' | 'error' | 'disabled' | 'unknown'
export type CameraProtocol = 'rtsp' | 'onvif' | 'http' | 'mock'

export interface Camera {
  id: string
  name: string
  description?: string
  manufacturer?: string
  model?: string
  ip_address?: string
  port?: number
  protocol: CameraProtocol
  location_id?: string
  recorder_id?: string
  status: CameraStatus
  is_active: boolean
  is_demo: boolean
  ai_enabled: boolean
  tags?: string[]
  stream_codec?: string
  stream_resolution?: string
  stream_fps?: number
  last_seen_at?: string
  last_error?: string
  created_at: string
}

export type EventStatus = 'new' | 'acknowledged' | 'assigned' | 'investigating' | 'resolved' | 'false_positive'
export type EventSeverity = 'low' | 'medium' | 'high' | 'critical'

export interface AIEvent {
  id: string
  camera_id: string
  rule_id?: string
  event_type: string
  status: EventStatus
  severity: EventSeverity
  confidence?: number
  model_version?: string
  is_simulated: boolean
  is_duplicate: boolean
  description?: string
  correlation_id?: string
  occurred_at: string
  acknowledged_at?: string
  resolved_at?: string
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface HealthResponse {
  status: string
  version: string
  database: string
  demo_mode: boolean
  services: Record<string, string>
}
