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
    // Strip YAML frontmatter (---\n...\n---) if present
    let stripped = translatedContent.replace(/^---[\s\S]*?---\s*\n?/, '');
    // Strip wrapping code fences (```markdown\n...\n```) that LLMs sometimes add
    stripped = stripped.replace(/^\s*```(?:markdown|md)?\s*\n([\s\S]*?)\n\s*```\s*$/, '$1');
    // Strip frontmatter again in case it was inside the code fence
    stripped = stripped.replace(/^---[\s\S]*?---\s*\n?/, '');
    const parts = stripped.split(/(```[\s\S]*?```)/g);
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
 * Handles headers, bold, italic, lists (unordered & ordered), tables,
 * horizontal rules, inline code, links, and paragraphs.
 */
function simpleMarkdownToHtml(md: string): string {
  const lines = md.split('\n');
  const output: string[] = [];
  let inTable = false;
  let inOrderedList = false;
  let inUnorderedList = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Horizontal rule
    if (/^---+\s*$/.test(line) || /^\*\*\*+\s*$/.test(line)) {
      closeOpenLists();
      output.push('<hr/>');
      continue;
    }

    // Headers
    if (line.startsWith('##### ')) { closeOpenLists(); output.push(`<h5>${inlineFormat(line.slice(6))}</h5>`); continue; }
    if (line.startsWith('#### ')) { closeOpenLists(); output.push(`<h4>${inlineFormat(line.slice(5))}</h4>`); continue; }
    if (line.startsWith('### ')) { closeOpenLists(); output.push(`<h3>${inlineFormat(line.slice(4))}</h3>`); continue; }
    if (line.startsWith('## ')) { closeOpenLists(); output.push(`<h2>${inlineFormat(line.slice(3))}</h2>`); continue; }
    if (line.startsWith('# ')) { closeOpenLists(); output.push(`<h1>${inlineFormat(line.slice(2))}</h1>`); continue; }

    // Table rows (lines starting with |)
    if (line.trim().startsWith('|')) {
      closeOpenLists();
      // Skip separator rows like |---|---|
      if (/^\|[\s-:|]+\|$/.test(line.trim())) continue;
      if (!inTable) {
        inTable = true;
        output.push('<table dir="rtl" style="width:100%; border-collapse:collapse; margin:1rem 0;">');
        // Check if this is a header row (next line is separator)
        const nextLine = i + 1 < lines.length ? lines[i + 1].trim() : '';
        const isHeader = /^\|[\s-:|]+\|$/.test(nextLine);
        const cells = line.split('|').filter(c => c.trim() !== '');
        const tag = isHeader ? 'th' : 'td';
        output.push('<tr>' + cells.map(c =>
          `<${tag} style="border:1px solid var(--ifm-color-emphasis-300); padding:0.5rem;">${inlineFormat(c.trim())}</${tag}>`
        ).join('') + '</tr>');
      } else {
        const cells = line.split('|').filter(c => c.trim() !== '');
        output.push('<tr>' + cells.map(c =>
          `<td style="border:1px solid var(--ifm-color-emphasis-300); padding:0.5rem;">${inlineFormat(c.trim())}</td>`
        ).join('') + '</tr>');
      }
      continue;
    } else if (inTable) {
      inTable = false;
      output.push('</table>');
    }

    // Unordered list items
    if (/^[-*]\s/.test(line)) {
      if (inOrderedList) { inOrderedList = false; output.push('</ol>'); }
      if (!inUnorderedList) { inUnorderedList = true; output.push('<ul>'); }
      output.push(`<li>${inlineFormat(line.replace(/^[-*]\s+/, ''))}</li>`);
      continue;
    }

    // Ordered list items
    const olMatch = line.match(/^(\d+)[.)]\s+(.+)/);
    if (olMatch) {
      if (inUnorderedList) { inUnorderedList = false; output.push('</ul>'); }
      if (!inOrderedList) { inOrderedList = true; output.push('<ol>'); }
      output.push(`<li>${inlineFormat(olMatch[2])}</li>`);
      continue;
    }

    // Close any open lists before non-list content
    closeOpenLists();

    // Empty lines are paragraph breaks
    if (line.trim() === '') {
      output.push('<br/>');
      continue;
    }

    // Regular paragraph
    output.push(`<p>${inlineFormat(line)}</p>`);
  }

  // Close any trailing open elements
  closeOpenLists();
  if (inTable) output.push('</table>');

  return output.join('\n');

  function closeOpenLists() {
    if (inUnorderedList) { inUnorderedList = false; output.push('</ul>'); }
    if (inOrderedList) { inOrderedList = false; output.push('</ol>'); }
  }
}

/**
 * Inline markdown formatting: bold, italic, inline code, links.
 */
function inlineFormat(text: string): string {
  return text
    // Inline code
    .replace(/`([^`]+)`/g, '<code style="direction:ltr;display:inline">$1</code>')
    // Links [text](url)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em>$1</em>');
}
