import type { WSEvent } from '@/types';

type EventHandler = (event: WSEvent) => void;

export class WSClient {
  private ws: WebSocket | null = null;
  private url: string;
  private handlers: Set<EventHandler> = new Set();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private pingTimer: ReturnType<typeof setInterval> | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private reconnectDelay = 1000;
  private maxReconnectDelay = 30000;
  private runId: string;
  private lastEventTimestamp: string | null = null;
  private intentionalDisconnect = false;
  private _state: 'disconnected' | 'connecting' | 'connected' = 'disconnected';

  get state() { return this._state; }

  constructor(runId: string) {
    const base = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    this.url = `${base}/ws/runs/${runId}`;
    this.runId = runId;
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    this.intentionalDisconnect = false;
    this._state = 'connecting';

    try {
      this.ws = new WebSocket(this.url);
    } catch {
      this.scheduleReconnect();
      return;
    }

    this.ws.onopen = () => {
      this._state = 'connected';
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
      this.startPing();

      // Request replay of missed events
      if (this.lastEventTimestamp) {
        this.ws?.send(JSON.stringify({
          type: 'replay',
          since: this.lastEventTimestamp,
        }));
      }
    };

    this.ws.onmessage = (msg) => {
      try {
        const event: WSEvent = JSON.parse(msg.data);

        if (event.type === 'pong') return;

        // Track last event timestamp for replay
        if (event.timestamp) {
          this.lastEventTimestamp = event.timestamp;
        }

        // Handle replay events
        if (event.type === 'replay' && Array.isArray((event as any).events)) {
          for (const replayEvent of (event as any).events) {
            this.handlers.forEach((h) => h(replayEvent));
          }
          return;
        }

        this.handlers.forEach((h) => h(event));
      } catch {
        // ignore malformed messages
      }
    };

    this.ws.onclose = (e) => {
      this._state = 'disconnected';
      this.stopPing();
      if (!this.intentionalDisconnect) {
        console.log(`[WS] Closed (${e.code}): ${e.reason || 'no reason'}`);
        this.scheduleReconnect();
      }
    };

    this.ws.onerror = () => {
      // onclose will fire after this
    };
  }

  disconnect() {
    this.intentionalDisconnect = true;
    this.stopPing();
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
    this._state = 'disconnected';
  }

  on(handler: EventHandler) {
    this.handlers.add(handler);
    return () => this.handlers.delete(handler);
  }

  private startPing() {
    this.pingTimer = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);
  }

  private stopPing() {
    if (this.pingTimer) clearInterval(this.pingTimer);
    this.pingTimer = null;
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log('[WS] Max reconnect attempts reached');
      return;
    }

    this.reconnectTimer = setTimeout(() => {
      this.reconnectAttempts++;
      this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
      console.log(`[WS] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts})`);
      this.connect();
    }, this.reconnectDelay);
  }
}
