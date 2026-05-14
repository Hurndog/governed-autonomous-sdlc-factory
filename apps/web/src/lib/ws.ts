import type { WSEvent } from '@/types';

type EventHandler = (event: WSEvent) => void;

export class WSClient {
  private ws: WebSocket | null = null;
  private url: string;
  private handlers: Set<EventHandler> = new Set();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private pingTimer: ReturnType<typeof setInterval> | null = null;
  private runId: string;

  constructor(runId: string) {
    const base = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    this.url = `${base}/ws/runs/${runId}`;
    this.runId = runId;
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log(`[WS] Connected to run ${this.runId}`);
      this.startPing();
    };

    this.ws.onmessage = (msg) => {
      try {
        const event: WSEvent = JSON.parse(msg.data);
        if (event.type === 'pong') return;
        this.handlers.forEach((h) => h(event));
      } catch {
        // ignore malformed messages
      }
    };

    this.ws.onclose = () => {
      console.log(`[WS] Disconnected from run ${this.runId}`);
      this.stopPing();
      this.scheduleReconnect();
    };

    this.ws.onerror = (err) => {
      console.error('[WS] Error:', err);
    };
  }

  disconnect() {
    this.stopPing();
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
  }

  on(handler: EventHandler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  private startPing() {
    this.pingTimer = setInterval(() => {
      this.ws?.send(JSON.stringify({ type: 'ping' }));
    }, 30000);
  }

  private stopPing() {
    if (this.pingTimer) clearInterval(this.pingTimer);
    this.pingTimer = null;
  }

  private scheduleReconnect() {
    this.reconnectTimer = setTimeout(() => this.connect(), 3000);
  }
}
