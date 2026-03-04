import React, { useState, useEffect, useCallback } from 'react';
import './chatbot.css';

interface PopupPosition {
  top: number;
  left: number;
}

export default function SelectedTextHandler(): React.JSX.Element | null {
  const [selectedText, setSelectedText] = useState('');
  const [showPopup, setShowPopup] = useState(false);
  const [position, setPosition] = useState<PopupPosition>({ top: 0, left: 0 });

  const handleSelection = useCallback(() => {
    const selection = window.getSelection();
    const text = selection?.toString().trim() || '';

    if (text.length > 10) {
      try {
        const range = selection!.getRangeAt(0);
        const rect = range.getBoundingClientRect();

        // Truncate very long selections
        const displayText = text.length > 2000
          ? text.substring(0, 2000) + '...'
          : text;

        setSelectedText(displayText);
        setPosition({
          top: rect.top + window.scrollY - 40,
          left: rect.left + window.scrollX + (rect.width / 2),
        });
        setShowPopup(true);
      } catch {
        // Selection may not have a valid range
        setShowPopup(false);
      }
    } else {
      setShowPopup(false);
      setSelectedText('');
    }
  }, []);

  useEffect(() => {
    // mouseup catches most desktop selections
    document.addEventListener('mouseup', handleSelection);

    return () => {
      document.removeEventListener('mouseup', handleSelection);
    };
  }, [handleSelection]);

  // Dismiss on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.closest('.selection-popup')) return;

      const selection = window.getSelection();
      if (!selection?.toString().trim()) {
        setShowPopup(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!showPopup) return null;

  return (
    <div
      className="selection-popup"
      style={{
        position: 'absolute',
        top: position.top,
        left: position.left,
        transform: 'translateX(-50%)',
        zIndex: 1200,
      }}
    >
      <button
        onClick={() => {
          window.dispatchEvent(
            new CustomEvent('askAboutSelection', { detail: selectedText })
          );
          setShowPopup(false);
          window.getSelection()?.removeAllRanges();
        }}
      >
        💬 Ask about this
      </button>
    </div>
  );
}
