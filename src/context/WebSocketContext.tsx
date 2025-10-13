import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from './AuthContext';

interface WebSocketMessage {
  type: string;
  [key: string]: unknown;
}

interface WebSocketContextType {
  isConnected: boolean;
  isConnecting: boolean;
  sendMessage: (message: Record<string, unknown>) => void;
  subscribe: (callback: (data: WebSocketMessage) => void) => () => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const subscribers = useRef<Set<(data: WebSocketMessage) => void>>(new Set());
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3 seconds
  const connectionStartTime = useRef<number | null>(null);

  const connect = useCallback(() => {
    if (!user) return;

    // Don't reconnect if already connected or connecting
    if (isConnected || isConnecting) return;

    // Clear any existing reconnection attempts
    if (reconnectTimeout.current) {
      clearTimeout(reconnectTimeout.current);
      reconnectTimeout.current = null;
    }

    setIsConnecting(true);

    try {
      // Close existing connection if any
      if (ws.current && ws.current.readyState !== WebSocket.CLOSED) {
        ws.current.close();
      }

      // Create new WebSocket connection
      const backendHost = window.location.hostname;
      const backendPort = '8000';
      const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${backendHost}:${backendPort}/ws/status/${user.id}/${user.role}/`;
      
      console.log('🔌 Connecting to WebSocket:', wsUrl);
      connectionStartTime.current = Date.now();
      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('✅ WebSocket connected successfully');
        setIsConnected(true);
        setIsConnecting(false);
        reconnectAttempts.current = 0; // Reset attempts on successful connection
        connectionStartTime.current = null;
      };

      ws.current.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          
          // Notify all subscribers
          subscribers.current.forEach(callback => {
            try {
              callback(data);
            } catch (error) {
              console.error('Error in WebSocket message handler:', error);
            }
          });
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onclose = (event) => {
        const wasConnected = isConnected;
        console.log('WebSocket disconnected', event.code, event.reason);
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
          console.log(`⏳ Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts}) in ${reconnectDelay/1000}s...`);
          
          reconnectTimeout.current = setTimeout(() => {
            reconnectTimeout.current = null;
            connect();
          }, reconnectDelay);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          console.log('WebSocket: Max reconnection attempts reached. Please refresh the page if you need real-time updates.');
        }
      };

      ws.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
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
  }, [user, isConnected, isConnecting]);

  // Connect when user logs in
  useEffect(() => {
    if (user) {
      connect();
    }

    // Cleanup on unmount or user change
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
  }, [user, connect]); // Only reconnect when user changes

  const sendMessage = useCallback((message: Record<string, unknown>) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected. Message not sent:', message);
    }
  }, []);

  const subscribe = useCallback((callback: (data: WebSocketMessage) => void) => {
    subscribers.current.add(callback);
    
    // Return unsubscribe function
    return () => {
      subscribers.current.delete(callback);
    };
  }, []);

  const value: WebSocketContextType = {
    isConnected,
    isConnecting,
    sendMessage,
    subscribe
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
};

// Custom hook for components that need WebSocket updates
export const useWebSocketSubscription = (callback: (data: WebSocketMessage) => void) => {
  const { subscribe, isConnected, isConnecting } = useWebSocketContext();

  useEffect(() => {
    const unsubscribe = subscribe(callback);
    return unsubscribe;
  }, [callback, subscribe]);

  return { isConnected, isConnecting };
};