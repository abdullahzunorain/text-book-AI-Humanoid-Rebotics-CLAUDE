import React from 'react';
import Content from '@theme-original/Navbar/Content';
import type ContentType from '@theme/Navbar/Content';
import type {WrapperProps} from '@docusaurus/types';
import AuthButton from '@site/src/components/AuthButton';

type Props = WrapperProps<typeof ContentType>;

/**
 * Wrapper around the original Navbar/Content to inject the AuthButton.
 * The AuthButton is positioned so it remains visible on both desktop and
 * mobile viewports (Docusaurus hides navbar items below 996px).
 */
export default function ContentWrapper(props: Props): React.JSX.Element {
  return (
    <div style={{display: 'flex', alignItems: 'center', width: '100%'}}>
      <div style={{flex: 1}}>
        <Content {...props} />
      </div>
      <div className="navbar__auth-button">
        <AuthButton />
      </div>
    </div>
  );
}
