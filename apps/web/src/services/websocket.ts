type WSMessage = { type: string; [key: string]: unknown }
type MessageHandler = (msg: WSMessage) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private handlers: Map<string, Set<MessageHandler>> = new Map()
  private reconnectTimer: any = null
  private reconnectDelay = 2000
  private maxReconnectDelay = 30000

  connect(token: string) {
    if (this.ws?.readyState === WebSocket.OPEN) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host || 'localhost:5173'
    const url = `${protocol}//${host}/ws?token=${encodeURIComponent(token)}`

    try {
      this.ws = new WebSocket(url)

      this.ws.onopen = () => {
        this.reconnectDelay = 2000
      }

      this.ws.onmessage = (event) => {
        try {
          const msg: WSMessage = JSON.parse(event.data)
          this.dispatch(msg)
        } catch {}
      }

      this.ws.onclose = () => {
        this.scheduleReconnect(token)
      }

      this.ws.onerror = () => {
        this.ws?.close()
      }
    } catch {
      this.scheduleReconnect(token)
    }
  }

  private scheduleReconnect(token: string) {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.reconnectTimer = setTimeout(() => {
      this.connect(token)
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay)
    }, this.reconnectDelay)
  }

  on(type: string, handler: MessageHandler) {
    if (!this.handlers.has(type)) this.handlers.set(type, new Set())
    this.handlers.get(type)!.add(handler)
    return () => this.off(type, handler)
  }

  off(type: string, handler: MessageHandler) {
    this.handlers.get(type)?.delete(handler)
  }

  private dispatch(msg: WSMessage) {
    this.handlers.get(msg.type)?.forEach((h) => h(msg))
    this.handlers.get('*')?.forEach((h) => h(msg))
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    this.ws?.close()
    this.ws = null
  }
}

export const wsService = new WebSocketService()
