import React, { useState, useEffect, useRef } from 'react';
import { useKanban } from '@/lib/context/KanbanContext';
import { authService } from '@/lib/services/auth';
import { apiService } from '@/lib/services/api';
import { MessageCircle, X, Send, Loader2, AlertTriangle } from 'lucide-react';

interface ChatMessage {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  kanbanUpdates?: any[];
}

export const ChatSidebar: React.FC = () => {
  const { board, loadBoard } = useKanban();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<WebSocket | null>(null);

  const toggleSidebar = () => setIsOpen(!isOpen);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const connectWebSocket = () => {
    if (socketRef.current) return;

    const token = authService.getToken();
    if (!token) return;

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.host}/ws/ai?token=${encodeURIComponent(token)}`);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log('WebSocket connection established');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'kanban_update') {
        loadBoard();
      }
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed');
      socketRef.current = null;
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  };

  useEffect(() => {
    if (isOpen) {
      connectWebSocket();
    }
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      content: inputValue,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiService.chatWithAI(inputValue, board?.id || '');

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        content: response.user_response.text,
        isUser: false,
        timestamp: new Date(),
        kanbanUpdates: response.kanban_updates || [],
      };

      setMessages(prev => [...prev, aiMessage]);

      if (response.kanban_updates && response.kanban_updates.length > 0) {
        loadBoard();
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <>
      {/* Chat toggle button */}
      <button
        onClick={toggleSidebar}
        className="fixed bottom-6 right-6 bg-purple-600 hover:bg-purple-700 text-white p-3 rounded-full shadow-lg z-40 transition-all"
        aria-label="Toggle chat"
      >
        <MessageCircle size={24} />
      </button>

      {/* Chat sidebar */}
      <div className={`fixed right-0 top-0 h-full w-80 bg-white shadow-xl transform transition-transform duration-300 ease-in-out z-50 ${isOpen ? 'translate-x-0' : 'translate-x-full'}`}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="bg-purple-600 text-white p-4 flex justify-between items-center">
            <h3 className="font-semibold">AI Assistant</h3>
            <button
              onClick={toggleSidebar}
              className="text-white hover:text-gray-200"
              aria-label="Close chat"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages container */}
          <div className="flex-1 p-4 overflow-y-auto bg-gray-50">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-gray-500">
                <MessageCircle size={48} className="mb-2" />
                <p>Start a conversation with your AI assistant</p>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`mb-4 flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs rounded-lg p-3 ${message.isUser ? 'bg-purple-600 text-white' : 'bg-gray-200 text-gray-800'}`}
                  >
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    <p className={`text-xs mt-1 ${message.isUser ? 'text-purple-200' : 'text-gray-500'}`}>
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                    {message.kanbanUpdates && message.kanbanUpdates.length > 0 && (
                      <div className="mt-2 text-xs bg-purple-100 text-purple-800 p-2 rounded">
                        <p>✨ AI made {message.kanbanUpdates.length} Kanban update{message.kanbanUpdates.length > 1 ? 's' : ''}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Error display */}
          {error && (
            <div className="p-2 bg-red-100 text-red-700 text-sm flex items-center">
              <AlertTriangle size={16} className="mr-2" />
              {error}
            </div>
          )}

          {/* Input area */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex gap-2">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message..."
                className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                rows={2}
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !inputValue.trim()}
                className={`p-3 rounded-lg ${isLoading || !inputValue.trim() ? 'bg-gray-300' : 'bg-purple-600 hover:bg-purple-700 text-white'}`}
                aria-label="Send message"
              >
                {isLoading ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
              </button>
            </div>
          </div>
        </div>
      </div>


    </>
  );
};