import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Snowfall Engineering',
  tagline: 'engineering.snowfalltravel.com',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://engineering.snowfalltravel.com',
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
    locales: ['en'],
  },

  presets: [
    [
      'redocusaurus',
      {
        // Plugin Options for loading OpenAPI files
        specs: [
          {
            id: 'junction-extensions-mobile-api',
            spec: 'openapi/junction/mobile_api/openapi.json',
          },
          {
            id: 'junction-go-data-api',
            spec: 'openapi/junction/data_api/openapi.yaml',
          },
          {
            id: 'junction-go-client-api',
            spec: 'openapi/junction/client_api/openapi.json',
          },
          {
            id: 'junction-pay-admin-api',
            spec: 'openapi/junction/pay_admin_api/openapi.json',
          },
          {
            id: 'junction-pay-pay-api',
            spec: 'openapi/junction/pay_api/openapi.json',
          },
          {
            id: 'junction-plus-poc-api',
            spec: 'openapi/junction/plus_poc_api/openapi.json',
          },
          {
            id: 'junction-hub-api',
            spec: 'openapi/junction/hub_api/openapi.json',
          },
          {
            id: 'junction-rocket-api',
            spec: 'openapi/junction/rocket_api/openapi.json',
          },
        ],
      },
    ],
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://git.snowfall.se/junction/junction/-/tree/main/docs/engineering',
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],
  themes: ['@docusaurus/theme-mermaid'],
  markdown: {
    mermaid: true,
  },
  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Snowfall Engineering',
        logo: {
          alt: 'Snowfall',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'onboarding',
            position: 'left',
            label: 'Onboarding',
          },
          {
            type: 'docSidebar',
            sidebarId: 'development',
            position: 'left',
            label: 'Development',
          },
          {
            type: 'docSidebar',
            sidebarId: 'monorepo',
            position: 'left',
            label: 'Monorepo',
          },
          {
            type: 'docSidebar',
            sidebarId: 'projects',
            position: 'left',
            label: 'Projects',
          },
          {
            type: 'docSidebar',
            sidebarId: 'specifications',
            position: 'left',
            label: 'Specifications',
          },
          {
            type: 'docSidebar',
            sidebarId: 'standard_library',
            position: 'left',
            label: 'Standard Library',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Snowfall Limited.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;
