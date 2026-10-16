import React, { useEffect, useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Camera,
  Grid,
  Bell,
  Brain,
  BarChart2,
  Users,
  Settings,
  LogOut,
  AlertTriangle,
  Volume2,
  VolumeX,
  ShieldAlert,
  Building2,
} from 'lucide-react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { authApi, eventsApi } from '../services/api'
import { wsService } from '../services/websocket'
import { soundAlert } from '../services/sound'
import IncidentAlertModal, { RealtimeIncident } from '../components/IncidentAlertModal'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Tổng quan', Icon: LayoutDashboard },
  { to: '/camera-wall', label: 'Màn hình Camera', Icon: Grid },
  { to: '/cameras', label: 'Quản lý Camera', Icon: Camera },
  { to: '/departments', label: 'Khoa phòng & Khu vực', Icon: Building2 },
  { to: '/alerts', label: 'Cảnh báo & Sự cố', Icon: Bell },
  { to: '/ai-rules', label: 'Quy tắc AI', Icon: Brain },
  { to: '/reports', label: 'Báo cáo', Icon: BarChart2 },
  { to: '/users', label: 'Người dùng', Icon: Users },
  { to: '/settings', label: 'Cài đặt', Icon: Settings },
]

export default function MainLayout() {
  const navigate = useNavigate()
  const qc = useQueryClient()
  const { data: user } = useQuery({ queryKey: ['me'], queryFn: authApi.me })

  const [currentIncident, setCurrentIncident] = useState<RealtimeIncident | null>(null)
  const [isMuted, setIsMuted] = useState(soundAlert.getMuted())

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) wsService.connect(token)

    // Listen to real-time incident broadcast from AI Computer Vision Worker
    const unsubIncident = wsService.on('ai.incident_alert', (msg: any) => {
      if (msg.incident) {
        const inc = msg.incident as RealtimeIncident
        if (inc.severity === 'critical' || inc.severity === 'high') {
          soundAlert.playEmergencyAlarm()
        } else {
          soundAlert.playNotificationChime()
        }
        setCurrentIncident(inc)
        qc.invalidateQueries({ queryKey: ['events'] })
        qc.invalidateQueries({ queryKey: ['events-recent'] })
        qc.invalidateQueries({ queryKey: ['metrics'] })
      }
    })

    const unsubUpdated = wsService.on('ai.event_updated', () => {
      qc.invalidateQueries({ queryKey: ['events'] })
      qc.invalidateQueries({ queryKey: ['metrics'] })
    })

    return () => {
      unsubIncident()
      unsubUpdated()
      wsService.disconnect()
    }
  }, [qc])

  const handleToggleMute = () => {
    const nextMuted = soundAlert.toggleMute()
    setIsMuted(nextMuted)
  }

  const handleTestAlarm = () => {
    soundAlert.playEmergencyAlarm()
    // Open a test incident popup
    setCurrentIncident({
      id: 'test-incident-' + Date.now(),
      camera_id: 'cam-demo-01',
      camera_name: 'Camera Cổng vào Cấp cứu (ER)',
      event_type: 'restricted_area',
      severity: 'critical',
      confidence: 0.94,
      occurred_at: new Date().toISOString(),
      description: 'Phát hiện đối tượng xâm nhập khu vực cách ly ngoài giờ cho phép.',
      is_simulated: true,
    })
  }

  const handleAcknowledgeIncident = async (id: string) => {
    try {
      if (!id.startsWith('test-')) {
        await eventsApi.acknowledge(id, 'Tiếp nhận trực tiếp qua popup giám sát')
      }
      qc.invalidateQueries({ queryKey: ['events'] })
    } catch (e) {
      console.error(e)
    }
  }

  const handleResolveIncident = async (id: string, isFp: boolean) => {
    try {
      if (!id.startsWith('test-')) {
        await eventsApi.resolve(id, isFp ? 'Báo động giả' : 'Đã kiểm tra an toàn', isFp)
      }
      qc.invalidateQueries({ queryKey: ['events'] })
    } catch (e) {
      console.error(e)
    }
  }

  const handleLogout = async () => {
    try {
      await authApi.logout()
    } catch {}
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    wsService.disconnect()
    navigate('/login')
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0f172a' }}>
      {/* Sidebar */}
      <nav
        style={{
          width: 240,
          background: '#1e293b',
          display: 'flex',
          flexDirection: 'column',
          borderRight: '1px solid #334155',
          flexShrink: 0,
        }}
      >
        <div style={{ padding: '20px 16px', borderBottom: '1px solid #334155' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ background: '#3b82f6', borderRadius: 8, padding: 6, display: 'flex' }}>
              <Camera size={18} color="white" />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 14, color: '#f8fafc' }}>AI Hospital</div>
              <div style={{ fontWeight: 400, fontSize: 11, color: '#94a3b8' }}>Camera v1.0</div>
            </div>
          </div>
          <div
            style={{
              marginTop: 10,
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: '#064e3b',
              border: '1px solid #059669',
              borderRadius: 6,
              padding: '4px 8px',
              fontSize: 11,
            }}
          >
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#34d399', display: 'inline-block', boxShadow: '0 0 6px #34d399' }} />
            <span style={{ color: '#34d399', fontWeight: 600, letterSpacing: '0.5px' }}>PRODUCTION (CHÍNH THỨC)</span>
          </div>
        </div>

        <div style={{ flex: 1, padding: '8px 0', overflowY: 'auto' }}>
          {NAV_ITEMS.map(({ to, label, Icon }) => (
            <NavLink
              key={to}
              to={to}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 10,
                padding: '10px 16px',
                textDecoration: 'none',
                color: isActive ? '#f8fafc' : '#94a3b8',
                background: isActive ? '#334155' : 'transparent',
                borderLeft: isActive ? '3px solid #3b82f6' : '3px solid transparent',
                fontSize: 14,
              })}
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </div>

        {/* Audio Alert Controls */}
        <div style={{ padding: '12px 16px', borderTop: '1px solid #334155', background: '#172033' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: 11, color: '#94a3b8', fontWeight: 600 }}>CHUÔNG CẢNH BÁO</span>
            <button
              onClick={handleToggleMute}
              title={isMuted ? 'Mở âm thanh chuông' : 'Tắt âm thanh chuông'}
              style={{
                background: 'transparent',
                border: 'none',
                color: isMuted ? '#ef4444' : '#22c55e',
                cursor: 'pointer',
                display: 'flex',
                padding: 2,
              }}
            >
              {isMuted ? <VolumeX size={15} /> : <Volume2 size={15} />}
            </button>
          </div>
          <button
            onClick={handleTestAlarm}
            style={{
              width: '100%',
              padding: '6px 10px',
              background: '#334155',
              border: '1px solid #475569',
              borderRadius: 6,
              color: '#f8fafc',
              fontSize: 11,
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
            }}
          >
            <ShieldAlert size={13} color="#f59e0b" /> Thử Chuông Báo Động
          </button>
        </div>

        {/* User profile & Logout */}
        <div style={{ padding: 16, borderTop: '1px solid #334155' }}>
          {user && (
            <div style={{ marginBottom: 10, fontSize: 12, color: '#94a3b8' }}>
              <div style={{ color: '#f8fafc', fontWeight: 600 }}>{user.full_name}</div>
              <div style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{user.email}</div>
            </div>
          )}
          <button
            onClick={handleLogout}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              width: '100%',
              padding: '8px 12px',
              background: '#dc2626',
              border: 'none',
              borderRadius: 6,
              color: 'white',
              fontSize: 13,
              cursor: 'pointer',
            }}
          >
            <LogOut size={14} /> Đăng xuất
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main style={{ flex: 1, overflow: 'auto', background: '#0f172a' }}>
        <Outlet />
      </main>

      {/* Realtime Incident Alert Modal */}
      <IncidentAlertModal
        incident={currentIncident}
        onAcknowledge={handleAcknowledgeIncident}
        onResolve={handleResolveIncident}
        onClose={() => setCurrentIncident(null)}
      />
    </div>
  )
}
