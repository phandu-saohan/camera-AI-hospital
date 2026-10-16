import React from 'react'
import { BarChart2, Download, Calendar } from 'lucide-react'

export default function ReportsPage() {
  return (
    <div style={{ padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: '#f8fafc', margin: 0 }}>
            Báo cáo & Thống kê Vận hành
          </h1>
          <p style={{ color: '#64748b', fontSize: 13, marginTop: 4 }}>
            Xuất dữ liệu sự kiện, thời gian phản hồi sự cố và lưu lượng người
          </p>
        </div>
        <button
          onClick={() => alert('Xuất báo cáo CSV thành công (dữ liệu demo)')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '8px 14px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: 6,
            fontSize: 13,
            cursor: 'pointer',
          }}
        >
          <Download size={14} /> Xuất CSV
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
        <ReportCard title="Tỷ lệ Báo động Đúng / Sai" metric="94.2%" desc="Độ chính xác xác nhận từ nhân viên điều dưỡng" />
        <ReportCard title="Thời gian Phản hồi TB" metric="1.8 phút" desc="Thời gian từ lúc AI phát hiện đến khi tiếp nhận" />
        <ReportCard title="Tổng lượt người qua cửa" metric="1,420 lượt" desc="Thống kê lưu lượng cửa cấp cứu trong ngày" />
      </div>
    </div>
  )
}

function ReportCard({ title, metric, desc }: { title: string; metric: string; desc: string }) {
  return (
    <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 10, padding: 18 }}>
      <div style={{ fontSize: 13, color: '#94a3b8' }}>{title}</div>
      <div style={{ fontSize: 28, fontWeight: 700, color: '#f8fafc', margin: '8px 0 4px' }}>{metric}</div>
      <div style={{ fontSize: 12, color: '#64748b' }}>{desc}</div>
    </div>
  )
}
