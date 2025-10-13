import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/context/AuthContext';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date | string; // Can be either Date object or string
}

interface ChatSuggestion {
  text: string;
  action: string;
}

interface ChatbotResponse {
  response: string;
  suggestions: string[];
  roleHints: string[];
}

const FloatingChatbot = () => {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<ChatSuggestion[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Role-based greetings
  const getGreeting = () => {
    if (!user) return '';
    
    const greetings: Record<string, string> = {
      customer: "Hi 👋 Need help tracking your service or signing off a job?",
      vendor: "Hey Pro! Want to request a customer signature or upload photos?",
      onboard_manager: "Would you like to review new vendor profiles?",
      ops_manager: "Need to resolve pending satisfaction signatures?",
      super_admin: "Welcome back. Manage system logs or assign roles?"
    };
    
    return greetings[user.role] || "Hello! How can I assist you today?";
  };

  // Format timestamp for display
  const formatTimestamp = (timestamp: Date | string): string => {
    try {
      // If it's already a Date object
      if (timestamp instanceof Date) {
        return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }
      
      // If it's a string, try to parse it as a date
      if (typeof timestamp === 'string') {
        const date = new Date(timestamp);
        if (!isNaN(date.getTime())) {
          return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
      }
      
      // Fallback to current time if parsing fails
      return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch (error) {
      // Fallback to current time if any error occurs
      return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  };

  // Initialize chat with greeting
  useEffect(() => {
    if (isOpen && messages.length === 0 && user) {
      const greetingMessage: Message = {
        id: 'greeting-' + Date.now(),
        text: getGreeting(),
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages([greetingMessage]);
      
      // Load conversation from localStorage
      const savedConversation = localStorage.getItem(`chatbot-conversation-${user.id}`);
      if (savedConversation) {
        try {
          const parsed: Message[] = JSON.parse(savedConversation);
          // Ensure timestamps are Date objects
          const messagesWithDates = parsed.map((msg) => ({
            ...msg,
            timestamp: typeof msg.timestamp === 'string' ? new Date(msg.timestamp) : msg.timestamp
          }));
          setMessages(messagesWithDates);
        } catch (e) {
          console.error('Failed to parse saved conversation', e);
        }
      }
      
      // Fetch initial suggestions
      fetchSuggestions();
    }
  }, [isOpen, user]);

  // Save conversation to localStorage
  useEffect(() => {
    if (user && messages.length > 0) {
      // Convert Date objects to strings for storage
      const messagesToSave = messages.map(msg => ({
        ...msg,
        timestamp: msg.timestamp instanceof Date ? msg.timestamp.toISOString() : msg.timestamp
      }));
      localStorage.setItem(`chatbot-conversation-${user.id}`, JSON.stringify(messagesToSave));
    }
  }, [messages, user]);

  // Scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSuggestions = async () => {
    if (!user) return;
    
    try {
      const response = await fetch(`/api/chat/context/?user_id=${user.id}&role=${user.role}`);
      if (response.ok) {
        const data = await response.json();
        if (data.context?.suggested_actions) {
          const chatSuggestions = data.context.suggested_actions.map((action: string) => ({
            text: action,
            action: action.toLowerCase().replace(/\s+/g, '_')
          }));
          setSuggestions(chatSuggestions);
        }
      } else {
        console.error('Failed to fetch suggestions:', response.status);
      }
    } catch (error) {
      console.error('Failed to fetch suggestions', error);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || !user || isLoading) return;

    // Add user message
    const userMessage: Message = {
      id: 'user-' + Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Send to backend
      const response = await fetch('/api/chatbot/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          role: user.role,
          message: inputValue
        })
      });

      if (response.ok) {
        const data: ChatbotResponse = await response.json();
        const botMessage: Message = {
          id: 'bot-' + Date.now(),
          text: data.response || "I'm not sure how to help with that.",
          sender: 'bot',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
        
        // Update suggestions
        if (data.suggestions) {
          const chatSuggestions = data.suggestions.map((suggestion: string) => ({
            text: suggestion,
            action: suggestion.toLowerCase().replace(/\s+/g, '_')
          }));
          setSuggestions(chatSuggestions);
        }
      } else {
        throw new Error('Failed to get response');
      }
    } catch (error) {
      console.error('Failed to send message', error);
      const errorMessage: Message = {
        id: 'error-' + Date.now(),
        text: "Sorry, I'm having trouble connecting. Please try again.",
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: ChatSuggestion) => {
    setInputValue(suggestion.text);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!user) return null;

  return (
    <>
      {/* Floating chat button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-blue-600 text-white shadow-lg hover:bg-blue-700 transition-all z-50 flex items-center justify-center"
        aria-label="Open chat"
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      </button>

      {/* Chat modal */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end justify-end p-4 sm:p-6"
            onClick={() => setIsOpen(false)}
          >
            <motion.div
              initial={{ y: 100, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 100, opacity: 0 }}
              transition={{ type: 'spring', damping: 20 }}
              className="w-full max-w-md h-[500px] bg-white rounded-lg shadow-xl flex flex-col"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Header */}
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
                <h3 className="font-semibold">InstaAssist AI</h3>
                <button 
                  onClick={() => setIsOpen(false)}
                  className="text-white hover:text-gray-200"
                  aria-label="Close chat"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </button>
              </div>

              {/* Messages container */}
              <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`mb-4 flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs md:max-w-md px-4 py-2 rounded-lg ${
                        message.sender === 'user'
                          ? 'bg-blue-500 text-white rounded-br-none'
                          : 'bg-gray-200 text-gray-800 rounded-bl-none'
                      }`}
                    >
                      <ReactMarkdown 
                        components={{
                          p: ({ node, ...props }) => <p className="text-sm" {...props} />,
                        }}
                      >
                        {message.text}
                      </ReactMarkdown>
                      <div className={`text-xs mt-1 ${message.sender === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                        {formatTimestamp(message.timestamp)}
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start mb-4">
                    <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg rounded-bl-none">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Suggestions */}
              {suggestions.length > 0 && (
                <div className="px-4 py-2 bg-gray-50 border-t border-gray-200">
                  <div className="flex flex-wrap gap-2">
                    {suggestions.slice(0, 3).map((suggestion, index) => (
                      <button
                        key={index}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full hover:bg-blue-200 transition-colors"
                      >
                        {suggestion.text}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Input area */}
              <div className="p-4 border-t border-gray-200">
                <div className="flex">
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message..."
                    className="flex-1 border border-gray-300 rounded-l-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    rows={1}
                    disabled={isLoading}
                  />
                  <button
                    onClick={sendMessage}
                    disabled={isLoading || !inputValue.trim()}
                    className={`bg-blue-500 text-white px-4 py-2 rounded-r-lg hover:bg-blue-600 transition-colors ${
                      (isLoading || !inputValue.trim()) ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                    </svg>
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default FloatingChatbot;