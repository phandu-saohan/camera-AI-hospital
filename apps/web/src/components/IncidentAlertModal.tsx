import React from 'react'
import { AlertTriangle, CheckCircle, XCircle, Volume2, VolumeX, ShieldAlert, X } from 'lucide-react'
import { soundAlert } from '../services/sound'

export interface RealtimeIncident {
  id: string
  camera_id: string
  camera_name?: string
  location_name?: string
  event_type: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  confidence?: number
  occurred_at: string
  description?: string
  is_simulated?: boolean
  snapshot_url?: string
}

interface IncidentAlertModalProps {
  incident: RealtimeIncident | null
  onAcknowledge: (id: string) => Promise<void>
  onResolve: (id: string, isFalsePositive: boolean) => Promise<void>
  onClose: () => void
}

export default function IncidentAlertModal({
  incident,
  onAcknowledge,
  onResolve,
  onClose,
}: IncidentAlertModalProps) {
  const [muted, setMuted] = React.useState(soundAlert.getMuted())
  const [submitting, setSubmitting] = React.useState(false)

  if (!incident) return null

  const isCritical = incident.severity === 'critical'
  const isHigh = incident.severity === 'high'
  const accentColor = isCritical ? '#ef4444' : isHigh ? '#f97316' : '#f59e0b'

  const handleToggleMute = () => {
    const nextMuted = soundAlert.toggleMute()
    setMuted(nextMuted)
  }

  const handleAcknowledge = async () => {
    setSubmitting(true)
    try {
      await onAcknowledge(incident.id)
      onClose()
    } finally {
      setSubmitting(false)
    }
  }

  const handleResolve = async (isFp: boolean) => {
    setSubmitting(true)
    try {
      await onResolve(incident.id, isFp)
      onClose()
    } finally {
      setSubmitting(false)
    }
  }

  const formatEventType = (type: string) => {
    switch (type) {
      case 'restricted_area':
        return 'XÂM NHẬP KHU VỰC CẤM'
      case 'fall_detection':
        return 'CẢNH BÁO TÉ NGÃ BỆNH NHÂN'
      case 'camera_tamper':
        return 'PHÁ HOẠI / CHE ỐNG KÍNH CAMERA'
      case 'people_counting':
        return 'LƯU LƯỢNG NGƯỜI VƯỢT NGƯỠNG'
      case 'queue_estimation':
        return 'ÙN TẮC HÀNG ĐỢI TIẾP ĐÓN'
      default:
        return type.replace(/_/g, ' ').toUpperCase()
    }
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 24,
        right: 24,
        zIndex: 9999,
        width: 440,
        maxWidth: 'calc(100vw - 32px)',
        background: '#1e293b',
        borderRadius: 14,
        border: `2px solid ${accentColor}`,
        boxShadow: `0 12px 36px rgba(0,0,0,0.65), 0 0 24px ${accentColor}44`,
        overflow: 'hidden',
        animation: 'slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
      }}
    >
      {/* Header */}
      <div
        style={{
          background: `${accentColor}22`,
          borderBottom: `1px solid ${accentColor}44`,
          padding: '12px 16px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              background: accentColor,
              borderRadius: 8,
              padding: 6,
              display: 'flex',
              color: 'white',
              boxShadow: `0 0 10px ${accentColor}`,
            }}
          >
            <ShieldAlert size={18} />
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#f8fafc', letterSpacing: 0.5 }}>
              CẢNH BÁO SỰ CỐ THỜI GIAN THỰC
            </div>
            <div style={{ fontSize: 11, color: '#94a3b8' }}>
              Mức độ: <strong style={{ color: accentColor }}>{incident.severity.toUpperCase()}</strong>
              {incident.is_simulated && (
                <span style={{ color: '#fbbf24', marginLeft: 6 }}>[DEMO]</span>
              )}
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <button
            onClick={handleToggleMute}
            title={muted ? 'Bật chuông âm thanh' : 'Tắt chuông âm thanh'}
            style={{
              background: 'transparent',
              border: 'none',
              color: muted ? '#94a3b8' : accentColor,
              cursor: 'pointer',
              padding: 4,
              display: 'flex',
            }}
          >
            {muted ? <VolumeX size={18} /> : <Volume2 size={18} />}
          </button>
          <button
            onClick={onClose}
            title="Đóng thông báo"
            style={{
              background: 'transparent',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              padding: 4,
              display: 'flex',
            }}
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Body */}
      <div style={{ padding: 16 }}>
        <div style={{ fontSize: 16, fontWeight: 700, color: '#f8fafc', marginBottom: 8 }}>
          {formatEventType(incident.event_type)}
        </div>

        <div style={{ fontSize: 13, color: '#cbd5e1', marginBottom: 12, lineHeight: 1.4 }}>
          {incident.description || 'Hệ thống AI vừa phát hiện sự kiện bất thường cần xác minh ngay.'}
        </div>

        <div
          style={{
            background: '#0f172a',
            borderRadius: 8,
            padding: '10px 12px',
            fontSize: 12,
            marginBottom: 16,
            border: '1px solid #334155',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
            <span style={{ color: '#64748b' }}>Camera:</span>
            <span style={{ color: '#f8fafc', fontWeight: 500 }}>
              {incident.camera_name || incident.camera_id}
            </span>
          </div>
          {incident.confidence && (
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
              <span style={{ color: '#64748b' }}>Độ tin cậy AI:</span>
              <span style={{ color: '#22c55e', fontWeight: 600 }}>
                {Math.round(incident.confidence * 100)}%
              </span>
            </div>
          )}
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#64748b' }}>Thời điểm:</span>
            <span style={{ color: '#94a3b8' }}>
              {new Date(incident.occurred_at).toLocaleTimeString('vi-VN')} (vừa xong)
            </span>
          </div>
        </div>

        {/* Snapshot preview if available */}
        {incident.snapshot_url && (
          <div style={{ marginBottom: 16, borderRadius: 8, overflow: 'hidden', border: '1px solid #334155' }}>
            <img
              src={incident.snapshot_url}
              alt="Bằng chứng AI"
              style={{ width: '100%', height: 160, objectFit: 'cover', display: 'block' }}
            />
          </div>
        )}

        {/* Action Buttons */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          <button
            onClick={handleAcknowledge}
            disabled={submitting}
            style={{
              padding: '10px 14px',
              background: '#2563eb',
              border: 'none',
              borderRadius: 8,
              color: 'white',
              fontSize: 13,
              fontWeight: 600,
              cursor: submitting ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
            }}
          >
            <CheckCircle size={16} /> Tiếp nhận ngay
          </button>
          <button
            onClick={() => handleResolve(true)}
            disabled={submitting}
            style={{
              padding: '10px 14px',
              background: '#334155',
              border: '1px solid #475569',
              borderRadius: 8,
              color: '#e2e8f0',
              fontSize: 13,
              fontWeight: 500,
              cursor: submitting ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 6,
            }}
          >
            <XCircle size={16} /> Báo động giả
          </button>
        </div>
      </div>
    </div>
  )
}
