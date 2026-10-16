// Web Audio API Synthesizer for Hospital Emergency and Warning Chimes
// No external audio files needed; 100% resilient and offline-capable.

class SoundAlertService {
  private ctx: AudioContext | null = null
  private isMuted: boolean = false

  constructor() {
    this.isMuted = localStorage.getItem('alert_sound_muted') === 'true'
  }

  private getContext(): AudioContext | null {
    if (typeof window === 'undefined') return null
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext
      if (AudioCtx) {
        this.ctx = new AudioCtx()
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {})
    }
    return this.ctx
  }

  public getMuted(): boolean {
    return this.isMuted
  }

  public setMuted(muted: boolean): void {
    this.isMuted = muted
    localStorage.setItem('alert_sound_muted', muted ? 'true' : 'false')
  }

  public toggleMute(): boolean {
    this.setMuted(!this.isMuted)
    return this.isMuted
  }

  // Play an urgent two-tone hospital emergency siren/beep (for CRITICAL / HIGH severity)
  public playEmergencyAlarm(): void {
    if (this.isMuted) return
    const ctx = this.getContext()
    if (!ctx) return

    const now = ctx.currentTime
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()

    osc.type = 'sawtooth'
    gain.gain.setValueAtTime(0.15, now)

    // Beep 1
    osc.frequency.setValueAtTime(880, now) // A5
    osc.frequency.setValueAtTime(659.25, now + 0.15) // E5
    gain.gain.setValueAtTime(0.15, now)
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3)

    // Beep 2
    osc.frequency.setValueAtTime(880, now + 0.35)
    osc.frequency.setValueAtTime(659.25, now + 0.5)
    gain.gain.setValueAtTime(0.15, now + 0.35)
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.7)

    osc.connect(gain)
    gain.connect(ctx.destination)

    osc.start(now)
    osc.stop(now + 0.72)
  }

  // Play a soft notification chime (for MEDIUM / LOW severity)
  public playNotificationChime(): void {
    if (this.isMuted) return
    const ctx = this.getContext()
    if (!ctx) return

    const now = ctx.currentTime
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()

    osc.type = 'sine'
    osc.frequency.setValueAtTime(523.25, now) // C5
    osc.frequency.exponentialRampToValueAtTime(659.25, now + 0.2) // E5

    gain.gain.setValueAtTime(0.1, now)
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4)

    osc.connect(gain)
    gain.connect(ctx.destination)

    osc.start(now)
    osc.stop(now + 0.42)
  }
}

export const soundAlert = new SoundAlertService()
