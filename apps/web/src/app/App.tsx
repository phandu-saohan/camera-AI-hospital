import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from '../features/auth/LoginPage'
import MainLayout from '../layouts/MainLayout'
import DashboardPage from '../features/dashboard/DashboardPage'
import CamerasPage from '../features/cameras/CamerasPage'
import CameraWallPage from '../features/camera-wall/CameraWallPage'
import AlertsPage from '../features/alerts/AlertsPage'
import AIRulesPage from '../features/ai-rules/AIRulesPage'
import ReportsPage from '../features/reports/ReportsPage'
import UsersPage from '../features/users/UsersPage'
import SettingsPage from '../features/settings/SettingsPage'
import DepartmentsPage from '../features/departments/DepartmentsPage'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('access_token')
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <MainLayout />
            </PrivateRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="cameras" element={<CamerasPage />} />
          <Route path="camera-wall" element={<CameraWallPage />} />
          <Route path="departments" element={<DepartmentsPage />} />
          <Route path="alerts" element={<AlertsPage />} />
          <Route path="ai-rules" element={<AIRulesPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="users" element={<UsersPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
