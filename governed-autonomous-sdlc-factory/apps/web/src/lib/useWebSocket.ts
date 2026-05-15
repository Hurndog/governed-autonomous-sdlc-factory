'use client';

import { useEffect, useRef, useCallback } from 'react';
import { useStore } from './store';

type WSEvent =
  | { type: 'pipeline.update'; data: Record<string, unknown> }
  | { type: 'replay.event'; data: Record<string, unknown> }
  | { type: 'governance.finding'; data: Record<string, unknown> }
  | { type: 'inference.trace'; data: Record<string, unknown> }
  | { type: 'integrity.alert'; data: Record<string, unknown> }
  | { type: 'token.usage'; data: Record<string, unknown> }
  | { type: 'health.update'; data: Record<string, unknown> };

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<NodeJS.Timeout>();
  const setWsConnected = useStore((s) => s.setWsConnected);
  const setHealth = useStore((s) => s.setHealth);
  const setPipelines = useStore((s) => s.setPipelines);
  const setReplaySessions = useStore((s) => s.setReplaySessions);
  const setGovernanceFindings = useStore((s) => s.setGovernanceFindings);
  const setModelStatuses = useStore((s) => s.setModelStatuses);

  const connect = useCallback(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/events`);
    wsRef.current = ws;

    ws.onopen = () => {
      setWsConnected(true);
      console.log('[WS] Connected');
    };

    ws.onmessage = (event) => {
      try {
        const msg: WSEvent = JSON.parse(event.data);
        handleMessage(msg);
      } catch (e) {
        console.error('[WS] Parse error:', e);
      }
    };

    ws.onclose = () => {
      setWsConnected(false);
      console.log('[WS] Disconnected, reconnecting in 3s...');
      reconnectRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [setWsConnected, setHealth, setPipelines, setReplaySessions, setGovernanceFindings, setModelStatuses]);

  function handleMessage(msg: WSEvent) {
    switch (msg.type) {
      case 'health.update':
        setHealth(msg.data as any);
        break;
      case 'pipeline.update':
        // Merge pipeline update into store
        break;
      case 'replay.event':
        // Append to replay session events
        break;
      case 'governance.finding':
        setGovernanceFindings([msg.data as any]);
        break;
      case 'token.usage':
        // Update token usage
        break;
    }
  }

  useEffect(() => {
    connect();
    return () => {
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return wsRef.current;
}
