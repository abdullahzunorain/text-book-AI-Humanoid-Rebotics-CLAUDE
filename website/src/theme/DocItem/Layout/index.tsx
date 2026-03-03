import React from 'react';
import Layout from '@theme-original/DocItem/Layout';
import type LayoutType from '@theme/DocItem/Layout';
import type {WrapperProps} from '@docusaurus/types';
import ChatbotWidget from '@site/src/components/ChatbotWidget';
import SelectedTextHandler from '@site/src/components/SelectedTextHandler';

type Props = WrapperProps<typeof LayoutType>;

export default function LayoutWrapper(props: Props): JSX.Element {
  return (
    <>
      <Layout {...props} />
      <ChatbotWidget />
      <SelectedTextHandler />
    </>
  );
}
