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
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 3; // Limit reconnection attempts
  const reconnectDelay = 5000; // 5 seconds
  const connectionStartTime = useRef<number | null>(null);

  const connect = useCallback(() => {
    if (!user) return;

    // Check if we've exceeded max reconnection attempts
    if (reconnectAttempts.current >= maxReconnectAttempts) {
      console.log(`WebSocket: Max reconnection attempts (${maxReconnectAttempts}) reached. Stopping reconnection.`);
      setIsConnecting(false);
      return;
    }

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
      // Backend is on port 8000, frontend on 8080
      const backendHost = window.location.hostname;
      const backendPort = '8000'; // Django backend port
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${backendHost}:${backendPort}/ws/status/${user.id}/${user.role}/`;
      
      console.log('Connecting to WebSocket:', wsUrl);
      connectionStartTime.current = Date.now();
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('WebSocket connected successfully');
        setIsConnected(true);
        setIsConnecting(false);
        reconnectAttempts.current = 0; // Reset attempts on successful connection
        connectionStartTime.current = null;
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
        const wasConnected = isConnected;
        console.log('WebSocket disconnected', event);
        setIsConnected(false);
        setIsConnecting(false);
        connectionStartTime.current = null;

        // If the connection was established for more than 30 seconds, reset reconnect attempts
        if (wasConnected && connectionStartTime.current) {
          const connectionDuration = Date.now() - connectionStartTime.current;
          if (connectionDuration > 30000) {
            reconnectAttempts.current = 0; // Reset if connection was stable for 30+ seconds
          }
        }

        // Only attempt to reconnect if:
        // 1. We haven't exceeded max attempts
        // 2. The close wasn't clean (code 1000) or was due to network issues (code 1006)
        // 3. We're not in the process of reconnecting already
        if (reconnectAttempts.current < maxReconnectAttempts && 
            (event.code === 1006 || event.code !== 1000) && 
            !reconnectTimeout.current) {
          reconnectAttempts.current += 1;
          console.log(`Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts}) in ${reconnectDelay/1000}s...`);
          
          reconnectTimeout.current = setTimeout(() => {
            reconnectTimeout.current = null;
            connect();
          }, reconnectDelay);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          console.log('WebSocket: Max reconnection attempts reached. Please refresh the page if you need real-time updates.');
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
        setIsConnecting(false);
        connectionStartTime.current = null;
        // Error will trigger onclose, which handles reconnection
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setIsConnecting(false);
      connectionStartTime.current = null;
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
      setIsConnected(false);
      setIsConnecting(false);
      reconnectAttempts.current = 0;
      connectionStartTime.current = null;
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