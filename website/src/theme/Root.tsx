import React from 'react';
import {AuthProvider} from '@site/src/components/AuthProvider';
import type {ReactNode} from 'react';

/**
 * Root theme component wrapping the entire Docusaurus app with AuthProvider.
 * See: https://docusaurus.io/docs/swizzling#wrapper-your-site-with-root
 */
export default function Root({children}: {children: ReactNode}): React.JSX.Element {
  return <AuthProvider>{children}</AuthProvider>;
}
