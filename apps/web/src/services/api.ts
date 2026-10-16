import axios, { AxiosInstance } from 'axios'
import type { Token, User, Camera, AIEvent, PaginatedResponse, HealthResponse } from '../types'

const BASE_URL = '/api/v1'

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401 && window.location.pathname !== '/login') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login: (email: string, password: string) =>
    api.post<Token>('/auth/login', { email, password }).then((r) => r.data),
  me: () => api.get<User>('/auth/me').then((r) => r.data),
  logout: () => api.post('/auth/logout').then((r) => r.data),
}

export const camerasApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<Camera>>('/cameras', { params }).then((r) => r.data),
  get: (id: string) => api.get<Camera>(`/cameras/${id}`).then((r) => r.data),
  create: (data: Record<string, unknown>) => api.post<Camera>('/cameras', data).then((r) => r.data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch<Camera>(`/cameras/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/cameras/${id}`),
  testConnection: (id: string) =>
    api.post(`/cameras/${id}/test-connection`).then((r) => r.data),
  health: () => api.get('/cameras/health').then((r) => r.data),
  healthHistory: (id: string) => api.get(`/cameras/${id}/health-history`).then((r) => r.data),
}

export const eventsApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<AIEvent>>('/events', { params }).then((r) => r.data),
  get: (id: string) => api.get<AIEvent>(`/events/${id}`).then((r) => r.data),
  acknowledge: (id: string, note?: string) =>
    api.post(`/events/${id}/acknowledge`, { note }).then((r) => r.data),
  assign: (id: string, assignee_id: string, note?: string) =>
    api.post(`/events/${id}/assign`, { assignee_id, note }).then((r) => r.data),
  resolve: (id: string, resolution: string, is_false_positive = false, note?: string) =>
    api.post(`/events/${id}/resolve`, { resolution, is_false_positive, note }).then((r) => r.data),
  evidence: (id: string) => api.get(`/events/${id}/evidence`).then((r) => r.data),
}

export const healthApi = {
  live: () => axios.get('/health/live').then((r) => r.data),
  ready: () => axios.get<HealthResponse>('/health/ready').then((r) => r.data),
  metrics: () => api.get('/metrics').then((r) => r.data),
}

export const notificationsApi = {
  getConfig: () => api.get('/notifications/config').then((r) => r.data),
  test: (data: { telegram_bot_token?: string; telegram_chat_id?: string; webhook_url?: string; message?: string }) =>
    api.post('/notifications/test', data).then((r) => r.data),
}

export const usersApi = {
  list: (params?: Record<string, unknown>) =>
    api.get<PaginatedResponse<User>>('/users', { params }).then((r) => r.data),
  get: (id: string) => api.get<User>(`/users/${id}`).then((r) => r.data),
  create: (data: Record<string, unknown>, role?: string) =>
    api.post<User>('/users', data, { params: { role_name: role } }).then((r) => r.data),
  update: (id: string, data: Record<string, unknown>, password?: string) =>
    api.patch<User>(`/users/${id}`, data, { params: { password } }).then((r) => r.data),
  delete: (id: string) => api.delete(`/users/${id}`),
  roles: () => api.get<Array<{ id: string; name: string; description?: string }>>('/users/roles').then((r) => r.data),
}

export const departmentsApi = {
  list: () => api.get<any[]>('/departments').then((r) => r.data),
  create: (data: Record<string, unknown>) => api.post('/departments', data).then((r) => r.data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/departments/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/departments/${id}`),
  locations: (deptId: string) => api.get<any[]>(`/departments/${deptId}/locations`).then((r) => r.data),
  createLocation: (data: Record<string, unknown>) => api.post('/departments/locations', data).then((r) => r.data),
  deleteLocation: (id: string) => api.delete(`/departments/locations/${id}`),
}

export const aiRulesApi = {
  list: (camera_id?: string) =>
    api.get<any[]>('/ai/rules', { params: { camera_id } }).then((r) => r.data),
  create: (data: Record<string, unknown>) => api.post('/ai/rules', data).then((r) => r.data),
  update: (id: string, data: Record<string, unknown>) =>
    api.patch(`/ai/rules/${id}`, data).then((r) => r.data),
  delete: (id: string) => api.delete(`/ai/rules/${id}`),
  status: () => api.get('/ai/status').then((r) => r.data),
  triggerScan: () => api.post('/ai/trigger-scan').then((r) => r.data),
}

export default api
