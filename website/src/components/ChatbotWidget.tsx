import React, { useState, useEffect, useRef, useCallback } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import './chatbot.css';

interface Message {
  role: 'user' | 'bot';
  content: string;
  sources?: string[];
}

export default function ChatbotWidget(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();
  const API_URL = (siteConfig.customFields?.apiUrl as string) || 'http://localhost:8000';
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'bot',
      content: 'Hi! I\'m your AI study companion. Ask me anything about the textbook content!',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when panel opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  // Listen for selected text events (US3)
  useEffect(() => {
    const handleSelection = (e: Event) => {
      const customEvent = e as CustomEvent<string>;
      const selectedText = customEvent.detail;
      if (selectedText) {
        setIsOpen(true);
        sendMessage(`Explain this: "${selectedText}"`, selectedText);
      }
    };
    window.addEventListener('askAboutSelection', handleSelection);
    return () => window.removeEventListener('askAboutSelection', handleSelection);
  }, []);

  const sendMessage = useCallback(async (text: string, selectedText?: string) => {
    const question = text.trim();
    if (!question) return;

    setError(null);
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          selected_text: selectedText || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Server error (${response.status})`);
      }

      const data = await response.json();
      setMessages(prev => [
        ...prev,
        {
          role: 'bot',
          content: data.answer,
          sources: data.sources,
        },
      ]);
    } catch (err: any) {
      const errorMessage = err.message?.includes('fetch')
        ? 'Unable to reach the chatbot server. Please try again later.'
        : err.message || 'Something went wrong. Please try again.';
      setError(errorMessage);
      setMessages(prev => [
        ...prev,
        {
          role: 'bot',
          content: `⚠️ ${errorMessage}`,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <>
      {/* Floating toggle button */}
      <button
        className="chatbot-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close chatbot' : 'Open chatbot'}
        title="AI Study Companion"
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div className="chatbot-panel">
          <div className="chatbot-header">
            <span className="chatbot-header-title">🤖 AI Study Companion</span>
            <button
              className="chatbot-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close chatbot"
            >
              ✕
            </button>
          </div>

          <div className="chatbot-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chatbot-message chatbot-message-${msg.role}`}>
                <div className="chatbot-message-content">
                  {msg.content}
                </div>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="chatbot-sources">
                    <small>📖 Sources: {msg.sources.join(', ')}</small>
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="chatbot-message chatbot-message-bot">
                <div className="chatbot-message-content chatbot-loading">
                  <span className="chatbot-dot"></span>
                  <span className="chatbot-dot"></span>
                  <span className="chatbot-dot"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="chatbot-input-area" onSubmit={handleSubmit}>
            <input
              ref={inputRef}
              type="text"
              className="chatbot-input"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about the textbook..."
              disabled={isLoading}
              maxLength={2000}
            />
            <button
              type="submit"
              className="chatbot-send"
              disabled={isLoading || !input.trim()}
              aria-label="Send message"
            >
              ➤
            </button>
          </form>
        </div>
      )}
    </>
  );
}
