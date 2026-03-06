import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'Learn ROS 2, sensor systems, and robot modeling — with an AI study companion',
  favicon: 'img/favicon.ico',

  future: {
    v4: false,
  },

  url: 'https://abdullahzunorain.github.io',
  baseUrl: '/text-book-AI-Humanoid-Rebotics-CLAUDE/',
  organizationName: 'abdullahzunorain',
  projectName: 'text-book-AI-Humanoid-Rebotics-CLAUDE',
  trailingSlash: false,

  onBrokenLinks: 'throw',

  customFields: {
    apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/abdullahzunorain/text-book-AI-Humanoid-Rebotics-CLAUDE/tree/main/website/',
        },
        blog: false, // Disabled — not needed for MVP
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/social-card.png',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    metadata: [
      {name: 'og:title', content: 'Physical AI & Humanoid Robotics Textbook'},
      {name: 'og:description', content: 'An interactive textbook covering Physical AI, ROS 2, and humanoid robotics with an embedded AI study companion.'},
      {name: 'og:type', content: 'website'},
    ],
    navbar: {
      title: 'Physical AI Textbook',
      logo: {
        alt: 'Physical AI Textbook Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'textbookSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {
          href: 'https://github.com/abdullahzunorain/text-book-AI-Humanoid-Rebotics-CLAUDE',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Content',
          items: [
            {
              label: 'Introduction',
              to: '/docs/intro',
            },
            {
              label: 'Module 1: ROS 2',
              to: '/docs/module1-ros2/architecture',
            },
            {
              label: 'Module 2: Simulation',
              to: '/docs/module2-simulation/chapter1-gazebo-basics',
            },
            {
              label: 'Module 3: NVIDIA Isaac',
              to: '/docs/module3-isaac/chapter1-isaac-sim-intro',
            },
            {
              label: 'Module 4: VLA Models',
              to: '/docs/module4-vla/chapter1-vla-intro',
            },
          ],
        },
        {
          title: 'Project',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/abdullahzunorain/text-book-AI-Humanoid-Rebotics-CLAUDE',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI Textbook. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'csharp', 'yaml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
