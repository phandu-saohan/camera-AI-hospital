import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { camerasApi } from '../../services/api'
import VideoPlayer from '../../components/VideoPlayer'
import { Monitor, AlertTriangle, RefreshCw, CheckCircle2, SlidersHorizontal, UserCheck } from 'lucide-react'
import type { Camera } from '../../types'

export default function CameraWallPage() {
  const [layout, setLayout] = useState<number>(4)
  const [selectedCameraId, setSelectedCameraId] = useState<string | null>(null)
  const [globalTracking, setGlobalTracking] = useState<boolean>(true)
  const [snapshotToast, setSnapshotToast] = useState<string | null>(null)

  const { data, refetch, isFetching } = useQuery({
    queryKey: ['camera-wall'],
    queryFn: () => camerasApi.list({ page_size: 16, is_active: true }),
    refetchInterval: 20000,
  })

  const cameras: Camera[] = data?.items || []

  const handleSnapshotCaptured = (dataUrl: string, camera: Camera) => {
    // Trigger automatic download
    const a = document.createElement('a')
    a.href = dataUrl
    a.download = `snapshot_${camera.name.replace(/\s+/g, '_')}_${Date.now()}.jpg`
    a.click()

    setSnapshotToast(`Đã chụp ảnh bằng chứng từ ${camera.name}`)
    setTimeout(() => setSnapshotToast(null), 3500)
  }

  const focusedCamera = selectedCameraId
    ? cameras.find((c) => c.id === selectedCameraId) || cameras[0]
    : null

  return (
    <div style={{ padding: 20, minHeight: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Toast Notification */}
      {snapshotToast && (
        <div
          style={{
            position: 'fixed',
            top: 20,
            right: 20,
            zIndex: 9999,
            background: '#15803d',
            color: 'white',
            padding: '10px 18px',
            borderRadius: 8,
            boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontSize: 13,
            fontWeight: 500,
          }}
        >
          <CheckCircle2 size={16} /> {snapshotToast}
        </div>
      )}

      {/* Header & Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, color: '#f8fafc', margin: 0 }}>
            Tường Camera Trực Tuyến (Camera Wall)
          </h1>
          <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>
            Giám sát đồng thời các luồng camera bệnh viện ({cameras.length} camera đang hoạt động)
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {selectedCameraId && (
            <button
              onClick={() => setSelectedCameraId(null)}
              style={{
                padding: '6px 12px',
                borderRadius: 6,
                border: '1px solid #3b82f6',
                background: '#1e3a8a',
                color: '#93c5fd',
                fontSize: 12,
                cursor: 'pointer',
                fontWeight: 600,
              }}
            >
              ← Quay lại Lưới {layout} ô
            </button>
          )}

          {/* Grid Layout Switcher */}
          <div style={{ display: 'flex', background: '#1e293b', padding: 3, borderRadius: 8, border: '1px solid #334155' }}>
            {[1, 4, 9, 16].map((n) => (
              <button
                key={n}
                onClick={() => {
                  setLayout(n)
                  setSelectedCameraId(null)
                }}
                style={{
                  padding: '5px 12px',
                  borderRadius: 6,
                  border: 'none',
                  background: layout === n && !selectedCameraId ? '#3b82f6' : 'transparent',
                  color: layout === n && !selectedCameraId ? '#fff' : '#94a3b8',
                  fontSize: 12,
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                {n} ô
              </button>
            ))}
          </div>

          {/* Master Person Tracking Toggle */}
          <button
            onClick={() => setGlobalTracking(!globalTracking)}
            title={globalTracking ? 'Tắt Theo Dõi Người trên toàn bộ camera' : 'Bật Theo Dõi Người trên toàn bộ camera'}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '6px 12px',
              borderRadius: 6,
              background: globalTracking ? 'rgba(5, 150, 105, 0.25)' : '#1e293b',
              border: globalTracking ? '1px solid #10b981' : '1px solid #475569',
              color: globalTracking ? '#34d399' : '#94a3b8',
              fontSize: 12,
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <UserCheck size={14} />
            <span>Tracking AI: {globalTracking ? 'BẬT' : 'TẮT'}</span>
          </button>

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            title="Làm mới danh sách luồng"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              padding: '6px 12px',
              borderRadius: 6,
              background: '#334155',
              border: 'none',
              color: '#f8fafc',
              fontSize: 12,
              cursor: isFetching ? 'not-allowed' : 'pointer',
            }}
          >
            <RefreshCw size={13} className={isFetching ? 'spin' : ''} />
            <span>Làm mới</span>
          </button>
        </div>
      </div>

      {/* Info Banner */}
      <div
        style={{
          background: '#0f172a',
          border: '1px solid #1e3a8a',
          borderRadius: 8,
          padding: '8px 14px',
          marginBottom: 16,
          display: 'flex',
          gap: 10,
          alignItems: 'center',
          fontSize: 12,
          color: '#93c5fd',
        }}
      >
        <SlidersHorizontal size={14} color="#3b82f6" />
        <span>
          <strong>Công nghệ Video:</strong> Luồng RTSP phân tích AI trực tiếp thời gian thực với tính năng <strong>Theo Dõi Người (Person Tracking MOT)</strong>: định danh đối tượng (#ID), đếm thời gian dừng (Dwell-time), vẽ quỹ đạo di chuyển và phát hiện bất thường.
        </span>
      </div>

      {/* Grid or Focused View */}
      {focusedCamera ? (
        <div style={{ flex: 1, minHeight: 480, display: 'flex' }}>
          <VideoPlayer
            camera={focusedCamera}
            streamType="main"
            isExpanded={true}
            onToggleExpand={() => setSelectedCameraId(null)}
            onSnapshot={handleSnapshotCaptured}
            enableTracking={globalTracking}
          />
        </div>
      ) : (
        <div
          style={{
            flex: 1,
            display: 'grid',
            gridTemplateColumns: `repeat(${Math.ceil(Math.sqrt(layout))}, 1fr)`,
            gap: 12,
          }}
        >
          {cameras.slice(0, layout).map((cam) => (
            <div key={cam.id} style={{ minHeight: 220 }}>
              <VideoPlayer
                camera={cam}
                streamType={layout <= 4 ? 'main' : 'sub'}
                isExpanded={false}
                onToggleExpand={() => setSelectedCameraId(cam.id)}
                onSnapshot={handleSnapshotCaptured}
                enableTracking={globalTracking}
              />
            </div>
          ))}

          {/* Placeholder if fewer cameras than grid */}
          {Array.from({ length: Math.max(0, layout - cameras.length) }).map((_, idx) => (
            <div
              key={`empty-${idx}`}
              style={{
                background: '#0f172a',
                border: '1px dashed #334155',
                borderRadius: 8,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: 220,
                color: '#64748b',
                fontSize: 12,
              }}
            >
              <Monitor size={28} color="#334155" style={{ marginBottom: 6 }} />
              <span>Kênh trống (Chưa gán camera)</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
