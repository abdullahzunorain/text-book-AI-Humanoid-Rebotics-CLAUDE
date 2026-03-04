import React from 'react';

/**
 * Props for the UrduContent component.
 */
interface UrduContentProps {
  /** Translated markdown content (Urdu prose with English code blocks) */
  translatedContent: string;
  /** Callback when user clicks "Read in English" */
  onShowEnglish: () => void;
}

/**
 * Renders translated Urdu content in RTL layout.
 * Code blocks within translated content get dir="ltr" override.
 */
export default function UrduContent({
  translatedContent,
  onShowEnglish,
}: UrduContentProps): React.JSX.Element {
  // Simple markdown rendering: convert code blocks to <pre><code>
  // and prose to paragraphs. For full markdown, a markdown renderer
  // would be ideal, but we keep it lightweight here.
  const renderContent = (): React.JSX.Element[] => {
    const parts = translatedContent.split(/(```[\s\S]*?```)/g);
    return parts.map((part, index) => {
      if (part.startsWith('```')) {
        // Extract language and code
        const match = part.match(/^```(\w*)\n?([\s\S]*?)```$/);
        const code = match ? match[2] : part.slice(3, -3);
        return (
          <pre
            key={index}
            dir="ltr"
            style={{textAlign: 'left', direction: 'ltr'}}>
            <code>{code}</code>
          </pre>
        );
      }
      // Regular prose — render as HTML with RTL
      return (
        <div
          key={index}
          dangerouslySetInnerHTML={{__html: simpleMarkdownToHtml(part)}}
        />
      );
    });
  };

  return (
    <div className="urdu-content" dir="rtl">
      <button
        onClick={onShowEnglish}
        className="button button--outline button--sm"
        style={{marginBottom: '1rem'}}
        type="button">
        Read in English
      </button>
      {renderContent()}
    </div>
  );
}

/**
 * Minimal markdown → HTML for translated prose.
 * Handles headers, bold, lists, and paragraphs.
 */
function simpleMarkdownToHtml(md: string): string {
  return md
    .split('\n')
    .map((line) => {
      // Headers
      if (line.startsWith('##### ')) return `<h5>${line.slice(6)}</h5>`;
      if (line.startsWith('#### ')) return `<h4>${line.slice(5)}</h4>`;
      if (line.startsWith('### ')) return `<h3>${line.slice(4)}</h3>`;
      if (line.startsWith('## ')) return `<h2>${line.slice(3)}</h2>`;
      if (line.startsWith('# ')) return `<h1>${line.slice(2)}</h1>`;
      // List items
      if (line.startsWith('- ')) return `<li>${line.slice(2)}</li>`;
      // Bold
      const boldified = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      // Empty lines are paragraph breaks
      if (boldified.trim() === '') return '<br/>';
      return `<p>${boldified}</p>`;
    })
    .join('\n');
}
