import React, {useState, useCallback} from 'react';
import Layout from '@theme-original/DocItem/Layout';
import type LayoutType from '@theme/DocItem/Layout';
import type {WrapperProps} from '@docusaurus/types';
import {useLocation} from '@docusaurus/router';
import ChatbotWidget from '@site/src/components/ChatbotWidget';
import SelectedTextHandler from '@site/src/components/SelectedTextHandler';
import UrduTranslateButton from '@site/src/components/UrduTranslateButton';
import UrduContent from '@site/src/components/UrduContent';
import PersonalizeButton from '@site/src/components/PersonalizeButton';
import PersonalizedContent from '@site/src/components/PersonalizedContent';

type Props = WrapperProps<typeof LayoutType>;

/**
 * Derive chapter slug from the current URL path.
 * e.g. /docs/module2-simulation/chapter1-gazebo-basics → module2-simulation/chapter1-gazebo-basics
 */
function useChapterSlug(): string {
  const location = useLocation();
  const path = location.pathname;
  // Strip /docs/ prefix and trailing slash
  const match = path.match(/\/docs\/(.+?)\/?\s*$/);
  return match ? match[1] : '';
}

export default function LayoutWrapper(props: Props): React.JSX.Element {
  const chapterSlug = useChapterSlug();
  const [isUrduActive, setIsUrduActive] = useState(false);
  const [translatedContent, setTranslatedContent] = useState<string>('');
  const [isPersonalizedActive, setIsPersonalizedActive] = useState(false);
  const [personalizedContent, setPersonalizedContent] = useState<string>('');

  const handleTranslated = useCallback(
    (content: string, _codeBlocks: string[]) => {
      setTranslatedContent(content);
      setIsUrduActive(true);
      // Deactivate personalization when switching to Urdu
      setIsPersonalizedActive(false);
      setPersonalizedContent('');
    },
    [],
  );

  const handleShowEnglish = useCallback(() => {
    setIsUrduActive(false);
    setTranslatedContent('');
  }, []);

  const handlePersonalized = useCallback((content: string) => {
    setPersonalizedContent(content);
    setIsPersonalizedActive(true);
    // Deactivate Urdu when switching to personalized
    setIsUrduActive(false);
    setTranslatedContent('');
  }, []);

  const handleShowOriginal = useCallback(() => {
    setIsPersonalizedActive(false);
    setPersonalizedContent('');
  }, []);

  return (
    <>
      {chapterSlug && (
        <div
          style={{
            padding: '0 var(--ifm-spacing-horizontal)',
            display: 'flex',
            gap: '0.5rem',
            flexWrap: 'wrap',
          }}>
          <UrduTranslateButton
            chapterSlug={chapterSlug}
            onTranslated={handleTranslated}
            onShowEnglish={handleShowEnglish}
            isUrduActive={isUrduActive}
          />
          <PersonalizeButton
            chapterSlug={chapterSlug}
            onPersonalized={handlePersonalized}
            onShowOriginal={handleShowOriginal}
            isPersonalizedActive={isPersonalizedActive}
          />
        </div>
      )}
      {isUrduActive && translatedContent ? (
        <div style={{padding: '0 var(--ifm-spacing-horizontal)'}}>
          <UrduContent
            translatedContent={translatedContent}
            onShowEnglish={handleShowEnglish}
          />
        </div>
      ) : isPersonalizedActive && personalizedContent ? (
        <div style={{padding: '0 var(--ifm-spacing-horizontal)'}}>
          <PersonalizedContent
            personalizedContent={personalizedContent}
            onShowOriginal={handleShowOriginal}
          />
        </div>
      ) : (
        <Layout {...props} />
      )}
      <ChatbotWidget />
      <SelectedTextHandler />
    </>
  );
}
