import React, { useState, useEffect } from 'react'
import {
  Settings,
  Shield,
  HardDrive,
  Cpu,
  Database,
  Send,
  Bell,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Lock,
} from 'lucide-react'
import { notificationsApi } from '../../services/api'

export default function SettingsPage() {
  const [loading, setLoading] = useState(false)
  const [testing, setTesting] = useState(false)
  const [testResult, setTestResult] = useState<any>(null)
  const [testError, setTestError] = useState<string | null>(null)

  // Configuration state
  const [telegramBotToken, setTelegramBotToken] = useState('')
  const [telegramChatId, setTelegramChatId] = useState('')
  const [webhookUrl, setWebhookUrl] = useState('')
  const [faceBlurEnabled, setFaceBlurEnabled] = useState(true)
  const [serverConfig, setServerConfig] = useState<any>(null)

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const data = await notificationsApi.getConfig()
      setServerConfig(data)
      if (data.telegram_chat_id) setTelegramChatId(data.telegram_chat_id)
      if (data.webhook_url) setWebhookUrl(data.webhook_url)
      if (typeof data.privacy_face_blur === 'boolean') {
        setFaceBlurEnabled(data.privacy_face_blur)
      }
    } catch (err: any) {
      console.warn('Không thể tải cấu hình thông báo:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleTestNotification = async () => {
    setTesting(true)
    setTestResult(null)
    setTestError(null)
    try {
      const res = await notificationsApi.test({
        telegram_bot_token: telegramBotToken.trim() || undefined,
        telegram_chat_id: telegramChatId.trim() || undefined,
        webhook_url: webhookUrl.trim() || undefined,
        message: '🔔 Thử nghiệm gửi cảnh báo từ Hệ thống AI Hospital Camera v1.0.',
      })
      setTestResult(res)
    } catch (err: any) {
      setTestError(err.response?.data?.detail || err.message || 'Lỗi gửi thông báo thử nghiệm')
    } finally {
      setTesting(false)
    }
  }

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: '#f8fafc', margin: '0 0 6px', display: 'flex', alignItems: 'center', gap: 10 }}>
          <Settings size={26} color="#3b82f6" />
          Cấu hình Hệ thống & Tự động hóa
        </h1>
        <p style={{ color: '#94a3b8', fontSize: 13, margin: 0 }}>
          Quản lý kênh thông báo thời gian thực, quy tắc bảo mật riêng tư y tế và hạ tầng AI / GPU
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: 20, marginBottom: 24 }}>
        {/* Kênh thông báo tự động (Telegram / Webhook) */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 12, padding: 22 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
            <div style={{ background: '#0284c722', borderRadius: 8, padding: 8, color: '#38bdf8' }}>
              <Bell size={20} />
            </div>
            <div>
              <div style={{ fontSize: 16, fontWeight: 600, color: '#f8fafc' }}>
                Kênh Cảnh báo Tự động (Telegram / Webhook)
              </div>
              <div style={{ fontSize: 12, color: '#94a3b8' }}>
                Tự động gửi thông báo tức thời & kèm ảnh bằng chứng khi có sự cố CRITICAL hoặc HIGH
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                Telegram Bot Token (tùy chọn / ghi đè .env)
              </label>
              <input
                type="password"
                placeholder={serverConfig?.telegram_enabled ? '•••••••••••••••• (Đã cấu hình trong .env)' : 'Ví dụ: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ'}
                value={telegramBotToken}
                onChange={(e) => setTelegramBotToken(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '9px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                Telegram Chat ID hoặc Channel ID
              </label>
              <input
                type="text"
                placeholder="Ví dụ: -1001234567890 hoặc @hospital_security_alerts"
                value={telegramChatId}
                onChange={(e) => setTelegramChatId(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '9px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 12, fontWeight: 500, color: '#cbd5e1', marginBottom: 6 }}>
                Zalo / Webhook URL (nhận JSON payload & cảnh báo)
              </label>
              <input
                type="url"
                placeholder="https://webhook.site/... hoặc endpoint tiếp nhận nội bộ"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                style={{
                  width: '100%',
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: '9px 12px',
                  color: '#f8fafc',
                  fontSize: 13,
                  outline: 'none',
                }}
              />
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginTop: 4 }}>
              <button
                type="button"
                onClick={handleTestNotification}
                disabled={testing}
                style={{
                  background: testing ? '#334155' : '#0284c7',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 6,
                  padding: '9px 16px',
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: testing ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                }}
              >
                {testing ? <Loader2 size={16} className="animate-spin" /> : <Send size={15} />}
                Gửi Thử nghiệm Cảnh báo
              </button>
              <span style={{ fontSize: 12, color: '#64748b' }}>
                Không làm gián đoạn luồng vận hành chính
              </span>
            </div>

            {testResult && (
              <div
                style={{
                  background: '#064e3b33',
                  border: '1px solid #059669',
                  borderRadius: 6,
                  padding: '10px 14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  fontSize: 13,
                  color: '#34d399',
                }}
              >
                <CheckCircle2 size={16} />
                <span>
                  Gửi thành công! Kết quả: Telegram: <strong>{testResult.results?.telegram}</strong>, Webhook: <strong>{testResult.results?.webhook}</strong>.
                </span>
              </div>
            )}

            {testError && (
              <div
                style={{
                  background: '#7f1d1d33',
                  border: '1px solid #dc2626',
                  borderRadius: 6,
                  padding: '10px 14px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  fontSize: 13,
                  color: '#f87171',
                }}
              >
                <AlertCircle size={16} />
                <span>Lỗi: {testError}</span>
              </div>
            )}
          </div>
        </div>

        {/* Bảo vệ Quyền riêng tư Y tế (Privacy Face Blur) */}
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 12, padding: 22, display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
            <div style={{ background: '#10b98122', borderRadius: 8, padding: 8, color: '#10b981' }}>
              <EyeOff size={20} />
            </div>
            <div>
              <div style={{ fontSize: 16, fontWeight: 600, color: '#f8fafc' }}>
                Bảo vệ Quyền riêng tư Bệnh nhân (Privacy Face Blur)
              </div>
              <div style={{ fontSize: 12, color: '#94a3b8' }}>
                Tuân thủ Nghị định 13/2023/NĐ-CP & Luật Khám bệnh, chữa bệnh
              </div>
            </div>
          </div>

          <p style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.6, margin: '0 0 16px' }}>
            Tự động làm mờ (Gaussian Blur) khuôn mặt người trong khu vực khám bệnh, phòng chờ và cấp cứu khi chụp ảnh snapshot bằng chứng sự cố. Đồng thời đóng dấu chứng nhận tính ẩn danh lên metadata ảnh.
          </p>

          <div
            style={{
              background: '#0f172a',
              border: '1px solid #334155',
              borderRadius: 8,
              padding: 16,
              marginBottom: 16,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, color: '#f8fafc' }}>
                Kích hoạt Bộ lọc Làm mờ Khuôn mặt
              </div>
              <div style={{ fontSize: 12, color: '#64748b', marginTop: 2 }}>
                Áp dụng cho mọi snapshot bằng chứng được lưu trữ hoặc gửi qua Telegram
              </div>
            </div>

            <button
              type="button"
              onClick={() => setFaceBlurEnabled(!faceBlurEnabled)}
              style={{
                background: faceBlurEnabled ? '#10b981' : '#475569',
                color: '#fff',
                border: 'none',
                borderRadius: 20,
                padding: '6px 14px',
                fontSize: 12,
                fontWeight: 600,
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
                transition: 'background 0.2s',
              }}
            >
              {faceBlurEnabled ? 'ĐANG BẬT' : 'ĐANG TẮT'}
            </button>
          </div>

          <div style={{ background: '#0f172a88', borderRadius: 8, padding: 14, border: '1px dashed #334155', marginTop: 'auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, fontWeight: 600, color: '#cbd5e1', marginBottom: 4 }}>
              <Lock size={14} color="#f59e0b" />
              Tiêu chuẩn Bảo mật Bằng chứng
            </div>
            <div style={{ fontSize: 12, color: '#64748b', lineHeight: 1.5 }}>
              Mọi snapshot đều được gán mã băm toàn vẹn SHA-256 trước khi ghi vào kho lưu trữ nội bộ. Ảnh gốc chưa qua làm mờ được cách ly nghiêm ngặt và chỉ truy cập được bởi Quản trị viên cấp cao khi có biên bản thanh tra.
            </div>
          </div>
        </div>
      </div>

      {/* Các thiết lập hạ tầng khác */}
      <h2 style={{ fontSize: 16, fontWeight: 600, color: '#cbd5e1', margin: '0 0 14px' }}>
        Hạ tầng Kỹ thuật & Tài nguyên Máy chủ
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 }}>
        <SettingCard
          icon={<Cpu size={20} />}
          title="Tăng tốc AI / GPU"
          desc="Tự động phát hiện NVIDIA T4 / TensorRT. Chế độ hiện tại: CPU Fallback (An toàn, YOLOv8n)."
        />
        <SettingCard
          icon={<HardDrive size={20} />}
          title="Chính sách Lưu trữ Bằng chứng"
          desc="Thời gian lưu trữ snapshot: 30 ngày. Video clip: 14 ngày. Xóa định kỳ tự động bằng Retention Worker."
        />
        <SettingCard
          icon={<Shield size={20} />}
          title="Bảo mật & Mã hóa RTSP"
          desc="Mã hóa URL RTSP server-side. Không mở cổng RTSP trực tiếp ra Internet. Tuân thủ tiêu chuẩn y tế."
        />
        <SettingCard
          icon={<Database size={20} />}
          title="Cơ sở Dữ liệu & Sao lưu"
          desc="PostgreSQL 16. Kịch bản sao lưu pg_dump tự động định kỳ vào 02:00 sáng hàng ngày."
        />
      </div>
    </div>
  )
}

function SettingCard({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 18 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10 }}>
        <div style={{ background: '#3b82f622', borderRadius: 8, padding: 8, color: '#3b82f6' }}>{icon}</div>
        <div style={{ fontSize: 14, fontWeight: 600, color: '#f8fafc' }}>{title}</div>
      </div>
      <p style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.5, margin: 0 }}>{desc}</p>
    </div>
  )
}
