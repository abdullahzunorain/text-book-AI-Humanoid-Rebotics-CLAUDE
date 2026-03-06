import React, {useState, useCallback} from 'react';
import {useAuth} from '@site/src/components/AuthProvider';

/**
 * Props for the UrduTranslateButton component.
 */
interface UrduTranslateButtonProps {
  /** Current chapter slug derived from the URL path */
  chapterSlug: string;
  /** Callback to pass translated content up to parent */
  onTranslated: (content: string, codeBlocks: string[]) => void;
  /** Callback when user wants to go back to English */
  onShowEnglish: () => void;
  /** Whether Urdu content is currently being displayed */
  isUrduActive: boolean;
}

const API_URL =
  (typeof window !== 'undefined' &&
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (window as any).__DOCUSAURUS_CUSTOM_FIELDS?.apiUrl) ||
  'http://localhost:8000';

/**
 * "اردو میں پڑھیں" toggle button — requires authentication.
 * Calls POST /api/translate with the current chapter slug.
 */
export default function UrduTranslateButton({
  chapterSlug,
  onTranslated,
  onShowEnglish,
  isUrduActive,
}: UrduTranslateButtonProps): React.JSX.Element | null {
  const {isAuthenticated} = useAuth();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const callTranslate = useCallback(async (forceRefresh = false) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_URL}/api/translate`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        credentials: 'include',
        body: JSON.stringify({chapter_slug: chapterSlug, force_refresh: forceRefresh}),
      });

      if (response.status === 401) {
        setError('Please sign in to read in Urdu.');
        return;
      }

      if (response.status === 429) {
        setError('Translation limit reached. Please wait a moment.');
        return;
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      onTranslated(data.translated_content, data.original_code_blocks);
    } catch {
      setError('Translation unavailable, please try again');
    } finally {
      setLoading(false);
    }
  }, [chapterSlug, onTranslated]);

  const handleClick = useCallback(async () => {
    if (isUrduActive) {
      onShowEnglish();
      return;
    }
    await callTranslate(false);
  }, [isUrduActive, onShowEnglish, callTranslate]);

  const handleRefresh = useCallback(async () => {
    await callTranslate(true);
  }, [callTranslate]);

  // Only render when authenticated (backend requires JWT)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div style={{marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap'}}>
      <button
        onClick={handleClick}
        disabled={loading}
        className="button button--secondary button--sm"
        style={{fontFamily: "'Noto Nastaliq Urdu', serif"}}
        type="button">
        {loading
          ? '⏳ ترجمہ ہو رہا ہے...'
          : isUrduActive
            ? 'Read in English'
            : 'اردو میں پڑھیں'}
      </button>
      {isUrduActive && !loading && (
        <button
          onClick={handleRefresh}
          disabled={loading}
          className="button button--outline button--secondary button--sm"
          title="Re-translate this chapter (bypasses cache)"
          type="button">
          ↺ Refresh Translation
        </button>
      )}
      {error && (
        <span
          style={{
            color: 'var(--ifm-color-danger)',
            fontSize: '0.875rem',
          }}>
          {error}
        </span>
      )}
    </div>
  );
}
