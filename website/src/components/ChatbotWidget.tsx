import React, { useState, useEffect, useRef, useCallback } from 'react';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import './chatbot.css';

interface Message {
  role: 'user' | 'bot';
  content: string;
  sources?: string[];
}

export default function ChatbotWidget(): React.JSX.Element {
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
  const [validationMsg, setValidationMsg] = useState<string | null>(null);
  const [selectedContext, setSelectedContext] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const historyLoadedRef = useRef(false);

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

  // Fetch chat history on mount (if authenticated)
  useEffect(() => {
    if (!isOpen || historyLoadedRef.current) return;
    historyLoadedRef.current = true;

    (async () => {
      try {
        const res = await fetch(`${API_URL}/api/chat/history?limit=50&offset=0`, {
          credentials: 'include',
        });
        if (res.status === 401) return; // Not authenticated — skip
        if (!res.ok) return;

        const data = await res.json();
        if (data.messages && data.messages.length > 0) {
          // Convert history (newest-first from API) to chronological order
          const historyMsgs: Message[] = [];
          for (const msg of [...data.messages].reverse()) {
            historyMsgs.push({ role: 'user', content: msg.question });
            historyMsgs.push({
              role: 'bot',
              content: msg.answer,
              sources: msg.sources || [],
            });
          }
          setMessages(prev => [...prev, ...historyMsgs]);
        }
      } catch {
        // Silently fail — history is a nice-to-have
      }
    })();
  }, [isOpen, API_URL]);

  // Keyboard accessibility: Escape key closes the panel
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  // Listen for selected text events (US6)
  useEffect(() => {
    const handleSelection = (e: Event) => {
      const customEvent = e as CustomEvent<string>;
      const selectedText = customEvent.detail;
      if (selectedText) {
        setIsOpen(true);
        setSelectedContext(selectedText);
        setTimeout(() => inputRef.current?.focus(), 100);
      }
    };
    window.addEventListener('askAboutSelection', handleSelection);
    return () => window.removeEventListener('askAboutSelection', handleSelection);
  }, []);

  const sendMessage = useCallback(async (text: string, selectedText?: string) => {
    const question = text.trim();
    if (!question) {
      setValidationMsg('Please enter a question before sending.');
      return;
    }

    // Use selectedContext if no explicit selectedText passed
    const contextText = selectedText || selectedContext || null;

    setValidationMsg(null);
    setError(null);
    setSelectedContext(null); // Clear after sending
    setMessages(prev => [...prev, { role: 'user', content: question }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          question,
          selected_text: contextText,
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
        <div className="chatbot-panel" role="dialog" aria-modal="true" aria-label="AI Study Companion chat">
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
            {selectedContext && (
              <div className="chatbot-selected-context">
                <span className="chatbot-context-label">📝 Selected text:</span>
                <span className="chatbot-context-text">
                  {selectedContext.length > 100
                    ? selectedContext.substring(0, 100) + '...'
                    : selectedContext}
                </span>
                <button
                  type="button"
                  className="chatbot-context-clear"
                  onClick={() => setSelectedContext(null)}
                  aria-label="Clear selection"
                >
                  ✕
                </button>
              </div>
            )}
            {validationMsg && (
              <div className="chatbot-validation" role="alert">
                {validationMsg}
              </div>
            )}
            <input
              ref={inputRef}
              type="text"
              className="chatbot-input"
              value={input}
              onChange={e => {
                setInput(e.target.value);
                if (validationMsg) setValidationMsg(null);
              }}
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
