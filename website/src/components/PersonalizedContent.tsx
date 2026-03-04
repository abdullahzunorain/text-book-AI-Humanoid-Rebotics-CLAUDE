import React from 'react';

/**
 * Props for the PersonalizedContent component.
 */
interface PersonalizedContentProps {
  /** Personalized markdown content from Gemini */
  personalizedContent: string;
  /** Callback when user clicks "Show Original" */
  onShowOriginal: () => void;
}

/**
 * Simple markdown → HTML converter for personalized content.
 * Handles headings, bold, italic, code blocks, lists, and links.
 */
function simpleMarkdownToHtml(md: string): string {
  let html = md;
  // Headings
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  // Line breaks → paragraphs
  html = html
    .split('\n\n')
    .map((p) => (p.trim() ? `<p>${p.trim()}</p>` : ''))
    .join('\n');
  return html;
}

/**
 * Renders personalized content with code blocks in LTR.
 * Shows a "Show Original" button to restore the default chapter view.
 */
export default function PersonalizedContent({
  personalizedContent,
  onShowOriginal,
}: PersonalizedContentProps): React.JSX.Element {
  const renderContent = (): React.JSX.Element[] => {
    const parts = personalizedContent.split(/(```[\s\S]*?```)/g);
    return parts.map((part, index) => {
      if (part.startsWith('```')) {
        // Extract language and code
        const match = part.match(/^```(\w*)\n?([\s\S]*?)```$/);
        const lang = match ? match[1] : '';
        const code = match ? match[2] : part.slice(3, -3);
        return (
          <pre key={index} dir="ltr" style={{textAlign: 'left', direction: 'ltr'}}>
            <code className={lang ? `language-${lang}` : undefined}>
              {code}
            </code>
          </pre>
        );
      }
      // Regular prose
      return (
        <div
          key={index}
          dangerouslySetInnerHTML={{__html: simpleMarkdownToHtml(part)}}
        />
      );
    });
  };

  return (
    <div className="personalized-content">
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          marginBottom: '1rem',
          padding: '0.5rem',
          background: 'var(--ifm-color-primary-lightest)',
          borderRadius: '4px',
          fontSize: '0.9rem',
        }}>
        <span>🎯 Personalized for your learning profile</span>
        <button
          onClick={onShowOriginal}
          className="button button--outline button--sm"
          type="button">
          Show Original
        </button>
      </div>
      {renderContent()}
    </div>
  );
}
