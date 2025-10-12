import { useState, useEffect, useRef } from 'react';
import { Send, Bot, X, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/context/AuthContext';
import { ENDPOINTS } from '@/services/endpoints';
import api from '@/services/api';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  type?: 'notification' | 'message';
}

interface RecentActivity {
  type: string;
  id: string;
  service?: string;
  status?: string;
  date?: string;
  name?: string;
  booking_id?: string;
  customer?: string;
  // Allow additional properties with unknown type
  [key: string]: string | number | boolean | undefined;
}

interface ContextData {
  role: string;
  suggested_actions: string[];
  recent_activities: RecentActivity[];
}

interface NotificationData {
  notification_type?: string;
  booking_id?: string;
  service_name?: string;
  customer_name?: string;
  vendor_name?: string;
  signature_id?: string;
  timestamp?: string;
  [key: string]: unknown;
}

interface WebSocketMessage {
  type: string;
  data: Record<string, string | undefined>;
}

export const ChatBot = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! How can I help you today?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [context, setContext] = useState<ContextData | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const { user } = useAuth();
  const { toast } = useToast();
  const ws = useRef<WebSocket | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Load context on mount
  useEffect(() => {
    if (user) {
      loadContext();
    }
  }, [user]);

  // Connect to WebSocket on mount
  useEffect(() => {
    if (user) {
      connectWebSocket();
    }

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [user]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  const loadContext = async () => {
    try {
      const response = await api.get(`${ENDPOINTS.CHAT}/context/`, {
        params: {
          user_id: user?.id,
          role: user?.role
        }
      });
      
      setContext(response.data.context);
    } catch (error) {
      console.error('Failed to load chat context:', error);
    }
  };

  const connectWebSocket = () => {
    if (!user) return;
    
    setIsConnecting(true);
    
    try {
      // Close existing connection if any
      if (ws.current) {
        ws.current.close();
      }
      
      // Create new WebSocket connection
      const wsUrl = `ws://localhost:8000/ws/chat/${user.id}/${user.role}/`;
      console.log('Connecting to WebSocket:', wsUrl);
      ws.current = new WebSocket(wsUrl);
      
      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnecting(false);
        
        // Add connection message
        addMessage({
          id: Date.now().toString(),
          text: 'Connected to support chat',
          sender: 'bot',
          timestamp: new Date(),
          type: 'notification'
        });
      };
      
      ws.current.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data);
          handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      ws.current.onclose = (event) => {
        console.log('WebSocket disconnected', event);
        setIsConnecting(false);
        addMessage({
          id: Date.now().toString(),
          text: 'Chat connection lost. Using fallback mode.',
          sender: 'bot',
          timestamp: new Date(),
          type: 'notification'
        });
      };
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnecting(false);
        addMessage({
          id: Date.now().toString(),
          text: 'Real-time chat unavailable. Using message mode.',
          sender: 'bot',
          timestamp: new Date(),
          type: 'notification'
        });
      };
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setIsConnecting(false);
      addMessage({
        id: Date.now().toString(),
        text: 'Chat service unavailable. You can still send messages.',
        sender: 'bot',
        timestamp: new Date(),
        type: 'notification'
      });
    }
  };

  const handleWebSocketMessage = (data: WebSocketMessage) => {
    switch (data.type) {
      case 'notification':
        // Type guard to ensure we have the required properties
        if (data.data && typeof data.data.notification_type === 'string') {
          handleNotification(data.data as NotificationData);
        }
        break;
      case 'bot_response':
        if (data.data && typeof data.data.message === 'string') {
          addMessage({
            id: Date.now().toString(),
            text: data.data.message,
            sender: 'bot',
            timestamp: new Date()
          });
        }
        break;
      default:
        console.log('Unknown WebSocket message type:', data.type);
    }
  };

  const handleNotification = (notificationData: NotificationData) => {
    const notificationType = notificationData.notification_type;
    let message = '';
    
    if (!notificationType) {
      message = 'You have a new notification.';
    } else {
      switch (notificationType) {
        case 'signature_requested':
          message = `Signature requested for booking ${notificationData.booking_id || 'N/A'}. Please check your email for the DocuSign link.`;
          break;
        case 'signature_completed':
          message = `Customer has signed for booking ${notificationData.booking_id || 'N/A'}. Payment is being processed.`;
          break;
        case 'booking_approved':
          message = `Booking ${notificationData.booking_id || 'N/A'} has been approved.`;
          break;
        case 'vendor_approved':
          message = 'Your vendor application has been approved! You can now start accepting jobs.';
          break;
        default:
          message = 'You have a new notification.';
      }
    }
    
    addMessage({
      id: Date.now().toString(),
      text: message,
      sender: 'bot',
      timestamp: new Date(),
      type: 'notification'
    });
    
    // Show toast notification
    toast({
      title: 'New Notification',
      description: message
    });
  };

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message]);
  };

  const handleSend = async () => {
    if (!input.trim() || !user) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input,
      sender: 'user',
      timestamp: new Date()
    };

    addMessage(userMessage);
    setInput('');

    try {
      // Send message via WebSocket if connected
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({
          type: 'user_message',
          data: {
            text: input,
            timestamp: new Date().toISOString()
          }
        }));
      } else {
        // Fallback to HTTP API
        console.log('Using HTTP API fallback');
        const response = await api.post(`${ENDPOINTS.CHAT}/query/`, {
          user_id: user.id,
          role: user.role,
          message: input
        });
        
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          sender: 'bot',
          timestamp: new Date()
        };
        addMessage(botMessage);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      };
      addMessage(errorMessage);
    }
  };

  const handleSuggestedAction = async (action: string) => {
    setInput(action);
    // Don't send automatically, let user review and send
  };

  const handleWorkflowAction = async (actionType: string) => {
    if (!user) return;
    
    try {
      // Send workflow event via WebSocket
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({
          type: 'workflow_event',
          data: {
            event_type: actionType,
            user_id: user.id,
            role: user.role,
            timestamp: new Date().toISOString()
          }
        }));
        
        addMessage({
          id: Date.now().toString(),
          text: `Processing ${actionType.replace('_', ' ')}...`,
          sender: 'bot',
          timestamp: new Date()
        });
      }
    } catch (error) {
      console.error('Failed to send workflow action:', error);
      toast({
        title: 'Action Failed',
        description: 'Failed to process your request',
        variant: 'destructive'
      });
    }
  };

  // Always render as a floating element
  return (
    <div className="fixed bottom-6 right-6 z-50">
      {!isOpen ? (
        <button
          onClick={() => setIsOpen(true)}
          className="bg-primary text-primary-foreground rounded-full p-4 shadow-lg hover:bg-primary/90 transition-all"
        >
          <MessageSquare className="h-6 w-6" />
        </button>
      ) : (
        <Card className="w-96 h-[600px] flex flex-col shadow-xl">
          <CardHeader className="p-4 border-b flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Bot className="h-5 w-5 text-primary" />
              Support Chat
            </CardTitle>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsOpen(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </CardHeader>

          <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.sender === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : message.type === 'notification'
                        ? 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                        : 'bg-muted'
                    }`}
                  >
                    <p className="text-sm">{message.text}</p>
                    <p className="text-xs opacity-70 mt-1">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>

          {/* Suggested Actions */}
          {context && context.suggested_actions.length > 0 && (
            <div className="px-4 py-2 border-t border-b">
              <p className="text-xs text-muted-foreground mb-2">Quick Actions:</p>
              <div className="flex flex-wrap gap-2">
                {context.suggested_actions.slice(0, 3).map((action, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    className="text-xs h-8"
                    onClick={() => handleSuggestedAction(action)}
                  >
                    {action}
                  </Button>
                ))}
              </div>
            </div>
          )}

          <div className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                disabled={isConnecting}
              />
              <Button onClick={handleSend} disabled={isConnecting || !input.trim()}>
                <Send className="h-4 w-4" />
              </Button>
            </div>
            {isConnecting && (
              <p className="text-xs text-muted-foreground mt-2">Connecting to chat service...</p>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};