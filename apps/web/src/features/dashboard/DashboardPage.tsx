import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { eventsApi, healthApi } from '../../services/api'
import { Camera, Wifi, WifiOff, Bell, Brain, AlertTriangle, Activity, Loader } from 'lucide-react'

export default function DashboardPage() {
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ['metrics'],
    queryFn: healthApi.metrics,
    refetchInterval: 15000,
  })
  const { data: events } = useQuery({
    queryKey: ['events-recent'],
    queryFn: () => eventsApi.list({ page: 1, page_size: 6 }),
    refetchInterval: 10000,
  })
  const { data: health } = useQuery({
    queryKey: ['health-ready'],
    queryFn: healthApi.ready,
    refetchInterval: 30000,
  })

  if (metricsLoading) return <LoadingState />

  const cams = metrics?.cameras || { total: 0, online: 0, offline: 0 }
  const evts = metrics?.events || { new: 0, today: 0 }

  return (
    <div style={{ padding: 24 }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f8fafc', margin: 0 }}>
          Tổng quan Trung tâm Giám sát Bệnh viện
        </h1>
        <p style={{ color: '#64748b', marginTop: 4, fontSize: 13 }}>
          Bảng điều khiển hoạt động camera & phân tích AI thời gian thực
        </p>
        {health?.demo_mode && (
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
              marginTop: 10,
              background: '#78350f',
              border: '1px solid #b45309',
              borderRadius: 6,
              padding: '4px 10px',
              fontSize: 12,
              color: '#fbbf24',
            }}
          >
            <AlertTriangle size={13} /> DỮ LIỆU ĐANG CHẠY Ở CHẾ ĐỘ MÔ PHỎNG (DEMO MODE)
          </div>
        )}
      </div>

      {/* Metrics Row */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 16,
          marginBottom: 24,
        }}
      >
        <StatCard icon={<Camera size={20} />} label="Tổng camera" value={cams.total} color="#3b82f6" />
        <StatCard icon={<Wifi size={20} />} label="Trực tuyến" value={cams.online} color="#22c55e" />
        <StatCard icon={<WifiOff size={20} />} label="Ngoại tuyến" value={cams.offline} color="#ef4444" />
        <StatCard icon={<Bell size={20} />} label="Sự cố mới" value={evts.new} color="#f59e0b" />
        <StatCard icon={<Activity size={20} />} label="Sự kiện hôm nay" value={evts.today} color="#8b5cf6" />
        <StatCard
          icon={<Brain size={20} />}
          label="AI Inference"
          value={health?.services?.ai_engine || 'cpu'}
          color="#06b6d4"
          isText
        />
      </div>

      {/* Detailed Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <Card title="Trạng thái Dịch vụ Hệ thống">
          <SystemStatus health={health} />
        </Card>
        <Card title="Sự kiện AI Gần đây">
          <RecentEvents events={events?.items || []} />
        </Card>
      </div>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
  color,
  isText = false,
}: {
  icon: React.ReactNode
  label: string
  value: number | string
  color: string
  isText?: boolean
}) {
  return (
    <div
      style={{
        background: '#1e293b',
        border: '1px solid #334155',
        borderRadius: 10,
        padding: 16,
        display: 'flex',
        alignItems: 'center',
        gap: 14,
      }}
    >
      <div style={{ background: `${color}22`, borderRadius: 8, padding: 10, color }}>{icon}</div>
      <div>
        <div style={{ fontSize: isText ? 15 : 24, fontWeight: 700, color: '#f8fafc' }}>{value}</div>
        <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>{label}</div>
      </div>
    </div>
  )
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 20 }}>
      <h3 style={{ fontSize: 15, fontWeight: 600, color: '#f8fafc', margin: '0 0 16px' }}>{title}</h3>
      {children}
    </div>
  )
}

function SystemStatus({ health }: { health?: any }) {
  if (!health) return <div style={{ color: '#64748b' }}>Đang tải trạng thái...</div>
  const items = [
    { label: 'API Backend', status: health.status },
    { label: 'Cơ sở dữ liệu (PostgreSQL)', status: health.database },
    ...Object.entries(health.services || {}).map(([k, v]) => ({ label: `Dịch vụ: ${k}`, status: String(v) })),
  ]
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {items.map(({ label, status }) => (
        <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: 13, color: '#94a3b8' }}>{label}</span>
          <StatusBadge status={status} />
        </div>
      ))}
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const isOk = status === 'ok' || status === 'alive'
  const isWarn = status === 'degraded' || status === 'cpu'
  const color = isOk ? '#22c55e' : isWarn ? '#f59e0b' : '#ef4444'
  return (
    <span
      style={{
        padding: '3px 10px',
        borderRadius: 20,
        fontSize: 11,
        fontWeight: 600,
        background: `${color}22`,
        color,
      }}
    >
      {status}
    </span>
  )
}

function RecentEvents({ events }: { events: any[] }) {
  if (events.length === 0) {
    return <div style={{ color: '#64748b', fontSize: 13 }}>Không có sự kiện mới phát sinh</div>
  }
  const severityColor: Record<string, string> = {
    critical: '#ef4444',
    high: '#f97316',
    medium: '#f59e0b',
    low: '#22c55e',
  }
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {events.map((ev) => {
        const sc = severityColor[ev.severity] || '#64748b'
        return (
          <div
            key={ev.id}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '8px 12px',
              background: '#0f172a',
              borderRadius: 8,
              border: `1px solid ${sc}33`,
            }}
          >
            <div>
              <div style={{ fontSize: 13, color: '#f8fafc', fontWeight: 500 }}>
                {ev.event_type.replace(/_/g, ' ').toUpperCase()}
                {ev.is_simulated && (
                  <span style={{ fontSize: 10, color: '#fbbf24', marginLeft: 6 }}>[DEMO]</span>
                )}
              </div>
              <div style={{ fontSize: 11, color: '#64748b', marginTop: 2 }}>
                {new Date(ev.occurred_at).toLocaleString('vi-VN')}
              </div>
            </div>
            <span
              style={{
                fontSize: 11,
                fontWeight: 600,
                padding: '2px 8px',
                borderRadius: 12,
                background: `${sc}22`,
                color: sc,
              }}
            >
              {ev.severity}
            </span>
          </div>
        )
      })}
    </div>
  )
}

function LoadingState() {
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '60vh',
        gap: 12,
        color: '#64748b',
      }}
    >
      <Loader size={24} /> Đang tải bảng điều khiển...
    </div>
  )
}
