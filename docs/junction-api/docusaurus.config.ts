import { themes as prismThemes } from 'prism-react-renderer'
import type { Config } from '@docusaurus/types'

const config: Config = {
  title: 'WELCOME TO THE DEVELOPER PORTAL',
  tagline:
    'Snowfall covers all verticals of the travel tech ecosystem. The following APIs will let you search, book and perform post-booking features according to the content you are looking for.',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://docs2.junction.travel',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',
  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en']
  },

  presets: [
    [
      'redocusaurus',
      {
      // Plugin Options for loading OpenAPI files
        specs: [
          {
            id: 'junction-api',
            spec: 'openapi/junction/rocket_api/openapi.yaml'
          }
        ]
      }
    ],
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js')
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css')
        }
      }
    ]
  ],
  themes: ['@docusaurus/theme-mermaid'],
  markdown: {
    mermaid: true
  },
  themeConfig: {
    navbar: {
      title: 'Junction',
      logo: {
        alt: 'Snowfall',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'guides',
          position: 'left',
          label: 'Guides'
        },
        {
          type: 'docSidebar',
          sidebarId: 'api',
          position: 'left',
          label: 'API Spec',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [],
      copyright: `Copyright © ${new Date().getFullYear()} Snowfall Limited.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
    docs: {
      sidebar: {
        hideable: true
      },
    },
  },
};

export default config
