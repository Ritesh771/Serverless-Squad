import { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/context/AuthContext';

interface WebSocketMessage {
  type: string;
  [key: string]: unknown;
}

export const useWebSocket = (onMessage: (data: WebSocketMessage) => void) => {
  const { user } = useAuth();
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    if (!user) return;

    // Clear any existing reconnection attempts
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }

    setIsConnecting(true);

    try {
      // Close existing connection if any
      if (ws.current) {
        ws.current.close();
      }

      // Create new WebSocket connection
      const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/status/${user.id}/${user.role}/`;
      console.log('Connecting to WebSocket:', wsUrl);
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setIsConnecting(false);
      };

      ws.current.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected', event);
        setIsConnected(false);
        setIsConnecting(false);

        // Attempt to reconnect after 5 seconds
        if (!reconnectTimeout.current) {
          reconnectTimeout.current = setTimeout(() => {
            console.log('Attempting to reconnect WebSocket...');
            connect();
          }, 5000);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
        setIsConnecting(false);
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setIsConnecting(false);
    }
  }, [user, onMessage]);

  useEffect(() => {
    if (user) {
      connect();
    }

    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, [user, connect]);

  const sendMessage = (message: Record<string, unknown>) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  return {
    isConnected,
    isConnecting,
    sendMessage,
    reconnect: connect
  };
};