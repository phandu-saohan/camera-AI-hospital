import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { eventsApi } from '../../services/api'
import type { AIEvent, EventSeverity } from '../../types'
import { Bell, CheckCircle, XCircle, AlertCircle, Loader } from 'lucide-react'

const SEVERITY_COLORS: Record<EventSeverity, string> = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#f59e0b',
  low: '#22c55e',
}

const SEVERITY_LABELS: Record<EventSeverity, string> = {
  critical: 'Khẩn cấp',
  high: 'Cao',
  medium: 'Trung bình',
  low: 'Thấp',
}

export default function AlertsPage() {
  const qc = useQueryClient()
  const [statusFilter, setStatusFilter] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['events', { page, status: statusFilter }],
    queryFn: () => eventsApi.list({ page, page_size: 20, status: statusFilter || undefined }),
    refetchInterval: 10000,
  })

  const acknowledgeMutation = useMutation({
    mutationFn: (id: string) => eventsApi.acknowledge(id, 'Nhân viên đã tiếp nhận qua web'),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['events'] }),
  })

  const resolveMutation = useMutation({
    mutationFn: ({ id, is_fp }: { id: string; is_fp: boolean }) =>
      eventsApi.resolve(id, is_fp ? 'Báo động giả' : 'Đã xử lý an toàn', is_fp),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['events'] }),
  })

  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f8fafc', margin: 0 }}>
            Cảnh báo & Xử lý Sự cố AI
          </h1>
          <p style={{ color: '#64748b', marginTop: 4, fontSize: 13 }}>
            Danh sách sự kiện bất thường được AI phát hiện thời gian thực ({data?.total || 0} sự kiện)
          </p>
        </div>
        <div style={{ display: 'flex', gap: 6 }}>
          {[
            { key: '', label: 'Tất cả' },
            { key: 'new', label: 'Chờ xử lý' },
            { key: 'acknowledged', label: 'Đã tiếp nhận' },
            { key: 'resolved', label: 'Đã hoàn tất' },
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => {
                setStatusFilter(key)
                setPage(1)
              }}
              style={{
                padding: '6px 12px',
                borderRadius: 6,
                border: '1px solid #334155',
                background: statusFilter === key ? '#3b82f6' : '#1e293b',
                color: statusFilter === key ? '#fff' : '#94a3b8',
                fontSize: 12,
                cursor: 'pointer',
              }}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>Đang tải danh sách sự cố...</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {(data?.items || []).map((ev) => (
            <EventRow
              key={ev.id}
              event={ev}
              onAcknowledge={() => acknowledgeMutation.mutate(ev.id)}
              onResolve={(is_fp) => resolveMutation.mutate({ id: ev.id, is_fp })}
              acknowledging={acknowledgeMutation.isPending}
              resolving={resolveMutation.isPending}
            />
          ))}
          {(data?.items || []).length === 0 && (
            <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>
              Không có cảnh báo nào trong mục này
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function EventRow({
  event,
  onAcknowledge,
  onResolve,
  acknowledging,
  resolving,
}: {
  event: AIEvent
  onAcknowledge: () => void
  onResolve: (is_fp: boolean) => void
  acknowledging: boolean
  resolving: boolean
}) {
  const sc = SEVERITY_COLORS[event.severity] || '#64748b'
  return (
    <div
      style={{
        background: '#1e293b',
        border: `1px solid ${sc}44`,
        borderRadius: 8,
        padding: 14,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <div style={{ background: `${sc}22`, borderRadius: 8, padding: 8, display: 'flex' }}>
          <Bell size={18} color={sc} />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 14, fontWeight: 600, color: '#f8fafc' }}>
              {event.event_type.replace(/_/g, ' ').toUpperCase()}
            </span>
            {event.is_simulated && (
              <span
                style={{
                  fontSize: 10,
                  color: '#fbbf24',
                  background: '#78350f',
                  padding: '2px 6px',
                  borderRadius: 4,
                }}
              >
                DEMO
              </span>
            )}
            <span
              style={{
                fontSize: 11,
                padding: '2px 8px',
                borderRadius: 12,
                background: `${sc}22`,
                color: sc,
                fontWeight: 600,
              }}
            >
              {SEVERITY_LABELS[event.severity] || event.severity}
            </span>
          </div>
          <div style={{ fontSize: 12, color: '#64748b', marginTop: 3 }}>
            Thời gian: {new Date(event.occurred_at).toLocaleString('vi-VN')} • Trạng thái: {event.status}
            {event.confidence && ` • Tin cậy: ${(event.confidence * 100).toFixed(0)}%`}
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', gap: 6 }}>
        {event.status === 'new' && (
          <button
            onClick={onAcknowledge}
            disabled={acknowledging}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              padding: '6px 12px',
              background: '#0e4429',
              border: '1px solid #22c55e',
              borderRadius: 6,
              color: '#22c55e',
              fontSize: 12,
              cursor: 'pointer',
            }}
          >
            <CheckCircle size={13} /> Tiếp nhận
          </button>
        )}
        {(event.status === 'new' || event.status === 'acknowledged' || event.status === 'assigned') && (
          <>
            <button
              onClick={() => onResolve(false)}
              disabled={resolving}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                padding: '6px 12px',
                background: '#1e3a5f',
                border: '1px solid #3b82f6',
                borderRadius: 6,
                color: '#3b82f6',
                fontSize: 12,
                cursor: 'pointer',
              }}
            >
              <CheckCircle size={13} /> Hoàn tất
            </button>
            <button
              onClick={() => onResolve(true)}
              disabled={resolving}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 4,
                padding: '6px 10px',
                background: '#3f1515',
                border: '1px solid #ef4444',
                borderRadius: 6,
                color: '#ef4444',
                fontSize: 12,
                cursor: 'pointer',
              }}
            >
              <XCircle size={13} /> Báo giả
            </button>
          </>
        )}
      </div>
    </div>
  )
}
