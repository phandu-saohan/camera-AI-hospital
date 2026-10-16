import React, { useEffect, useRef, useState } from 'react'
import Hls from 'hls.js'
import {
  Camera,
  Maximize2,
  Minimize2,
  Volume2,
  VolumeX,
  RefreshCw,
  Camera as CameraIcon,
  Wifi,
  WifiOff,
  Radio,
  Sliders,
  UserCheck,
} from 'lucide-react'
import type { Camera as CameraType } from '../types'

interface VideoPlayerProps {
  camera: CameraType
  streamType?: 'main' | 'sub'
  onSnapshot?: (dataUrl: string, camera: CameraType) => void
  isExpanded?: boolean
  onToggleExpand?: () => void
  enableTracking?: boolean
}

export default function VideoPlayer({
  camera,
  streamType = 'main',
  onSnapshot,
  isExpanded = false,
  onToggleExpand,
  enableTracking = true,
}: VideoPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const hlsRef = useRef<Hls | null>(null)
  const pcRef = useRef<RTCPeerConnection | null>(null)
  const animationFrameRef = useRef<number | null>(null)

  const [activeStream, setActiveStream] = useState<'main' | 'sub'>(streamType)
  const [streamProtocol, setStreamProtocol] = useState<'mjpeg' | 'webrtc' | 'hls' | 'canvas'>(
    camera.is_demo || camera.status === 'offline' || camera.protocol === 'mock' ? 'canvas' : 'mjpeg'
  )
  const [isTracking, setIsTracking] = useState<boolean>(enableTracking)
  const [isMuted, setIsMuted] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [streamError, setStreamError] = useState<string | null>(null)
  const [fps, setFps] = useState<number>(camera.stream_fps || 25)

  useEffect(() => {
    setIsTracking(enableTracking)
  }, [enableTracking])

  // Demo / offline check
  const isDemoOrOffline = camera.is_demo || camera.status === 'offline' || camera.protocol === 'mock'

  // Build MediaMTX streaming URLs based on standard camera stream path
  const streamKey = `cam_${camera.id}_${activeStream}`
  const hlsUrl = `http://${window.location.hostname}:8888/${streamKey}/index.m3u8`
  const whepUrl = `http://${window.location.hostname}:8889/${streamKey}/whep`

  // Start stream playback
  useEffect(() => {
    let isCancelled = false

    const cleanupStreams = () => {
      if (hlsRef.current) {
        hlsRef.current.destroy()
        hlsRef.current = null
      }
      if (pcRef.current) {
        pcRef.current.close()
        pcRef.current = null
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
        animationFrameRef.current = null
      }
    }

    cleanupStreams()
    setStreamError(null)

    if (isDemoOrOffline) {
      setStreamProtocol('canvas')
    } else {
      // Physical camera with RTSP: stream directly via FastAPI MJPEG gateway
      setStreamProtocol('mjpeg')
      setIsLoading(false)
    }

    return () => {
      isCancelled = true
      cleanupStreams()
    }
  }, [camera.id, activeStream, camera.status, isDemoOrOffline])

  // Dedicated effect to start canvas animation whenever streamProtocol is 'canvas' and canvasRef is mounted
  useEffect(() => {
    if (streamProtocol === 'canvas') {
      startCanvasSimulation()
    }
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
        animationFrameRef.current = null
      }
    }
  }, [streamProtocol, camera.status, camera.is_demo])

  // Canvas-based simulation for Demo / Offline / Fallback
  const startCanvasSimulation = () => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let personX = 80
    let personDirection = 1
    let frameCount = 0

    const render = () => {
      frameCount++
      const width = canvas.width
      const height = canvas.height

      // Background
      if (camera.status === 'offline') {
        ctx.fillStyle = '#0b0f19'
        ctx.fillRect(0, 0, width, height)

        // Offline noise pattern
        ctx.fillStyle = '#1e293b'
        ctx.font = 'bold 16px monospace'
        ctx.textAlign = 'center'
        ctx.fillText('CAMERA NGOẠI TUYẾN (NO SIGNAL)', width / 2, height / 2 - 10)
        ctx.font = '12px sans-serif'
        ctx.fillStyle = '#64748b'
        ctx.fillText('Vui lòng kiểm tra cáp PoE hoặc kết nối NVR', width / 2, height / 2 + 16)
      } else {
        // Gradient room simulation (Hospital Ward / Corridor)
        const grad = ctx.createLinearGradient(0, 0, width, height)
        grad.addColorStop(0, '#131b2e')
        grad.addColorStop(0.5, '#1e293b')
        grad.addColorStop(1, '#0f172a')
        ctx.fillStyle = grad
        ctx.fillRect(0, 0, width, height)

        // Grid floor lines for perspective
        ctx.strokeStyle = 'rgba(51, 65, 85, 0.4)'
        ctx.lineWidth = 1
        for (let i = 0; i < width; i += 40) {
          ctx.beginPath()
          ctx.moveTo(i, height * 0.4)
          ctx.lineTo((i - width / 2) * 2 + width / 2, height)
          ctx.stroke()
        }

        // Horizontal perspective lines
        for (let y = height * 0.4; y < height; y += (height - y) * 0.25 + 10) {
          ctx.beginPath()
          ctx.moveTo(0, y)
          ctx.lineTo(width, y)
          ctx.stroke()
        }

        // Animated simulated person walking
        personX += 1.2 * personDirection
        if (personX > width - 120 || personX < 60) {
          personDirection *= -1
        }
        const personY = height * 0.35 + 20
        const personW = 44
        const personH = 90

        // Person silhouette
        ctx.fillStyle = '#475569'
        // Head
        ctx.beginPath()
        ctx.arc(personX + personW / 2, personY + 16, 12, 0, Math.PI * 2)
        ctx.fill()
        // Body
        ctx.fillRect(personX + 8, personY + 28, personW - 16, 44)
        // Legs
        ctx.fillRect(personX + 10, personY + 72, 8, 20)
        ctx.fillRect(personX + personW - 18, personY + 72, 8, 20)

        // AI Person Tracking overlay
        if (isTracking) {
          const cornerLen = 12
          ctx.strokeStyle = '#22c55e'
          ctx.lineWidth = 2

          // Corner brackets
          ctx.beginPath()
          // Top-Left
          ctx.moveTo(personX, personY + cornerLen)
          ctx.lineTo(personX, personY)
          ctx.lineTo(personX + cornerLen, personY)
          // Top-Right
          ctx.moveTo(personX + personW - cornerLen, personY)
          ctx.lineTo(personX + personW, personY)
          ctx.lineTo(personX + personW, personY + cornerLen)
          // Bottom-Left
          ctx.moveTo(personX, personY + personH - cornerLen)
          ctx.lineTo(personX, personY + personH)
          ctx.lineTo(personX + cornerLen, personY + personH)
          // Bottom-Right
          ctx.moveTo(personX + personW - cornerLen, personY + personH)
          ctx.lineTo(personX + personW, personY + personH)
          ctx.lineTo(personX + personW, personY + personH - cornerLen)
          ctx.stroke()

          // Track ID Badge above person
          ctx.fillStyle = '#0f172a'
          ctx.fillRect(personX - 4, personY - 22, 110, 18)
          ctx.strokeStyle = '#22c55e'
          ctx.lineWidth = 1
          ctx.strokeRect(personX - 4, personY - 22, 110, 18)

          ctx.fillStyle = '#22c55e'
          ctx.beginPath()
          ctx.arc(personX + 4, personY - 13, 3, 0, Math.PI * 2)
          ctx.fill()

          ctx.fillStyle = '#ffffff'
          ctx.font = 'bold 10px monospace'
          ctx.textAlign = 'left'
          ctx.fillText('#ID 01 | 94%', personX + 12, personY - 9)

          // Dwell time & Movement status pill below
          const dwellSeconds = Math.floor(frameCount / 25)
          const dwellStr = `00:${String(dwellSeconds % 60).padStart(2, '0')}s`
          ctx.fillStyle = 'rgba(15, 23, 42, 0.9)'
          ctx.fillRect(personX - 4, personY + personH + 4, 110, 16)
          ctx.strokeStyle = '#334155'
          ctx.strokeRect(personX - 4, personY + personH + 4, 110, 16)

          ctx.fillStyle = '#34d399'
          ctx.font = '9px monospace'
          ctx.fillText(`DI CHUYỂN (${dwellStr})`, personX + 4, personY + personH + 16)

          // Top Right HUD
          ctx.fillStyle = 'rgba(15, 23, 42, 0.85)'
          ctx.fillRect(width - 210, 36, 196, 22)
          ctx.strokeStyle = '#22c55e'
          ctx.strokeRect(width - 210, 36, 196, 22)

          ctx.fillStyle = '#22c55e'
          ctx.beginPath()
          ctx.arc(width - 198, 47, 4, 0, Math.PI * 2)
          ctx.fill()

          ctx.fillStyle = '#f8fafc'
          ctx.font = 'bold 10px monospace'
          ctx.fillText('TRACKING: 1 NGƯỜI | TỔNG: 1', width - 186, 51)
        }
      }

      // CCTV Overlay: Camera Name, Location & Live Watermark
      ctx.textAlign = 'left'
      ctx.font = 'bold 12px monospace'
      ctx.fillStyle = '#f8fafc'
      ctx.fillText(`CAM: ${camera.name}`, 14, 24)

      // Timestamp overlay with milliseconds
      const now = new Date()
      const timeStr = `${now.toLocaleDateString('vi-VN')} ${now.toLocaleTimeString('vi-VN')}.${String(
        now.getMilliseconds()
      ).padStart(3, '0')}`
      ctx.fillText(timeStr, 14, 42)

      // Live Indicator
      ctx.textAlign = 'right'
      if (camera.status === 'online') {
        const pulse = Math.sin(frameCount * 0.1) > 0
        ctx.fillStyle = pulse ? '#ef4444' : '#991b1b'
        ctx.beginPath()
        ctx.arc(width - 70, 20, 5, 0, Math.PI * 2)
        ctx.fill()
        ctx.fillStyle = '#f8fafc'
        ctx.fillText(camera.is_demo ? 'LIVE [DEMO]' : 'LIVE', width - 14, 24)
      } else {
        ctx.fillStyle = '#ef4444'
        ctx.fillText('DISCONNECTED', width - 14, 24)
      }

      // Codec and resolution banner at bottom
      ctx.textAlign = 'left'
      ctx.font = '10px monospace'
      ctx.fillStyle = '#64748b'
      const resText = `${camera.stream_resolution || '1920x1080'} | ${activeStream.toUpperCase()} | ${camera.stream_codec || 'H.264'} | ${fps} FPS`
      ctx.fillText(resText, 14, height - 12)

      animationFrameRef.current = requestAnimationFrame(render)
    }

    render()
  }

  // Snapshot capture handler
  const handleCaptureSnapshot = () => {
    if (streamProtocol === 'mjpeg') {
      const a = document.createElement('a')
      a.href = `/api/v1/cameras/${camera.id}/live-frame?stream_type=${activeStream}&t=${Date.now()}`
      a.download = `snapshot_${camera.name.replace(/\s+/g, '_')}_${Date.now()}.jpg`
      a.click()
      return
    }

    let dataUrl: string | null = null

    if (streamProtocol === 'canvas' && canvasRef.current) {
      dataUrl = canvasRef.current.toDataURL('image/jpeg', 0.9)
    } else if (videoRef.current) {
      const offscreen = document.createElement('canvas')
      offscreen.width = videoRef.current.videoWidth || 640
      offscreen.height = videoRef.current.videoHeight || 360
      const ctx = offscreen.getContext('2d')
      if (ctx) {
        ctx.drawImage(videoRef.current, 0, 0, offscreen.width, offscreen.height)
        dataUrl = offscreen.toDataURL('image/jpeg', 0.9)
      }
    }

    if (dataUrl) {
      if (onSnapshot) {
        onSnapshot(dataUrl, camera)
      } else {
        // Direct download
        const a = document.createElement('a')
        a.href = dataUrl
        a.download = `snapshot_${camera.name.replace(/\s+/g, '_')}_${Date.now()}.jpg`
        a.click()
      }
    }
  }

  // Toggle Fullscreen
  const handleToggleFullscreen = () => {
    if (!containerRef.current) return
    if (!document.fullscreenElement) {
      containerRef.current.requestFullscreen().catch(() => {})
      setIsFullscreen(true)
    } else {
      document.exitFullscreen().catch(() => {})
      setIsFullscreen(false)
    }
  }

  return (
    <div
      ref={containerRef}
      style={{
        position: 'relative',
        width: '100%',
        height: '100%',
        minHeight: 220,
        background: '#090d16',
        borderRadius: 8,
        overflow: 'hidden',
        border: '1px solid #334155',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Top Bar Overlay */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          padding: '8px 12px',
          background: 'linear-gradient(180deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0) 100%)',
          zIndex: 10,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          pointerEvents: 'none',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, pointerEvents: 'auto' }}>
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              background: camera.status === 'online' ? '#22c55e' : '#ef4444',
              display: 'inline-block',
              boxShadow: camera.status === 'online' ? '0 0 8px #22c55e' : 'none',
            }}
          />
          <span style={{ fontSize: 13, fontWeight: 600, color: '#f8fafc', textShadow: '0 1px 2px #000' }}>
            {camera.name}
          </span>
          {camera.is_demo && (
            <span
              style={{
                fontSize: 10,
                padding: '1px 6px',
                borderRadius: 4,
                background: '#78350f',
                color: '#fbbf24',
                fontWeight: 600,
                border: '1px solid #b45309',
              }}
            >
              DEMO
            </span>
          )}
          {camera.ai_enabled && (
            <span
              style={{
                fontSize: 10,
                padding: '1px 6px',
                borderRadius: 4,
                background: '#1e3a8a',
                color: '#60a5fa',
                fontWeight: 600,
                border: '1px solid #2563eb',
              }}
            >
              AI ON
            </span>
          )}
          {isTracking && (
            <span
              style={{
                fontSize: 10,
                padding: '1px 6px',
                borderRadius: 4,
                background: '#064e3b',
                color: '#34d399',
                fontWeight: 600,
                border: '1px solid #059669',
                display: 'flex',
                alignItems: 'center',
                gap: 4,
              }}
            >
              <span
                style={{
                  width: 5,
                  height: 5,
                  borderRadius: '50%',
                  background: '#34d399',
                  boxShadow: '0 0 6px #34d399',
                }}
              />
              TRACKING ON
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 6, pointerEvents: 'auto' }}>
          {/* Main / Sub stream switch */}
          <button
            onClick={() => setActiveStream(activeStream === 'main' ? 'sub' : 'main')}
            title="Chuyển đổi Luồng Chính (Full HD) / Luồng Phụ (SD)"
            style={{
              background: 'rgba(30, 41, 59, 0.8)',
              border: '1px solid #475569',
              color: '#e2e8f0',
              borderRadius: 4,
              padding: '2px 8px',
              fontSize: 11,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            {activeStream.toUpperCase()}
          </button>
        </div>
      </div>

      {/* Main Video / Canvas Surface */}
      <div style={{ position: 'relative', flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#090d16' }}>
        {streamProtocol === 'mjpeg' ? (
          <img
            src={`/api/v1/cameras/${camera.id}/live-feed?stream_type=${activeStream}&tracking=${isTracking}`}
            alt={camera.name}
            onError={() => {
              setStreamProtocol('canvas')
            }}
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        ) : streamProtocol === 'webrtc' || streamProtocol === 'hls' ? (
          <video
            ref={videoRef}
            muted={isMuted}
            playsInline
            autoPlay
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        ) : (
          <canvas
            ref={canvasRef}
            width={640}
            height={360}
            style={{ width: '100%', height: '100%', objectFit: 'contain' }}
          />
        )}
      </div>

      {/* Bottom Control Bar on Hover */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          padding: '8px 12px',
          background: 'linear-gradient(0deg, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0) 100%)',
          zIndex: 10,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          opacity: 0.95,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#94a3b8' }}>
          <Radio size={12} color={camera.status === 'online' ? '#22c55e' : '#ef4444'} />
          <span>
            {streamProtocol === 'mjpeg'
              ? 'RTSP Trực tiếp (Live)'
              : streamProtocol === 'webrtc'
              ? 'WebRTC (WHEP)'
              : streamProtocol === 'hls'
              ? 'HLS Live'
              : 'Mô phỏng (Canvas)'}
          </span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {/* Tracking toggle button */}
          <button
            onClick={() => setIsTracking(!isTracking)}
            title={isTracking ? 'Tắt Theo dõi Người (Tracking: Đang BẬT)' : 'Bật Theo dõi Người (Tracking: Đang TẮT)'}
            style={{
              ...actionBtnStyle,
              background: isTracking ? 'rgba(5, 150, 105, 0.4)' : 'rgba(30, 41, 59, 0.85)',
              border: isTracking ? '1px solid #10b981' : '1px solid #475569',
              color: isTracking ? '#34d399' : '#94a3b8',
            }}
          >
            <UserCheck size={14} />
          </button>

          {/* Snapshot button */}
          <button
            onClick={handleCaptureSnapshot}
            title="Chụp ảnh khung hình bằng chứng"
            style={actionBtnStyle}
          >
            <CameraIcon size={14} />
          </button>

          {/* Mute button */}
          <button
            onClick={() => setIsMuted(!isMuted)}
            title={isMuted ? 'Bật âm thanh' : 'Tắt âm thanh'}
            style={actionBtnStyle}
          >
            {isMuted ? <VolumeX size={14} /> : <Volume2 size={14} />}
          </button>

          {/* Expand/Single view */}
          {onToggleExpand && (
            <button
              onClick={onToggleExpand}
              title={isExpanded ? 'Thu nhỏ lưới' : 'Phóng to một camera'}
              style={actionBtnStyle}
            >
              {isExpanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
            </button>
          )}

          {/* Fullscreen */}
          <button
            onClick={handleToggleFullscreen}
            title="Toàn màn hình"
            style={actionBtnStyle}
          >
            <Maximize2 size={14} />
          </button>
        </div>
      </div>
    </div>
  )
}

const actionBtnStyle: React.CSSProperties = {
  background: 'rgba(30, 41, 59, 0.85)',
  border: '1px solid #475569',
  color: '#f8fafc',
  borderRadius: 6,
  padding: '6px',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  cursor: 'pointer',
}
