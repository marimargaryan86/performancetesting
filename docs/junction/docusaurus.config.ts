import { themes as prismThemes } from "prism-react-renderer";
import type { Config } from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";

const config: Config = {
  title: "WELCOME TO THE DEVELOPER PORTAL",
  tagline:
    "Snowfall covers all verticals of the travel tech ecosystem. The following APIs will let you search, book and perform post-booking features according to the content you are looking for.",
  favicon: "img/favicon.ico",

  url: "https://docs.junction.travel",
  baseUrl: "/",
  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  presets: [
    [
      "redocusaurus",
      {
        specs: [
          {
            id: "client-api",
            spec: "openapi/junction/client_api/openapi.json",
          },
        ],
      },
    ],
    [
      "classic",
      {
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
        },
        theme: {
          customCss: require.resolve("./src/css/custom.css"),
        },
      },
    ],
  ],
  themes: ["@docusaurus/theme-mermaid"],
  markdown: {
    mermaid: true,
  },
  themeConfig: {
    navbar: {
      title: "Junction",
      logo: {
        alt: "Snowfall",
        src: "img/logo.svg",
      },
      items: [
        {
          type: "docSidebar",
          sidebarId: "guides",
          position: "left",
          label: "Guides",
        },
        {
          type: "docSidebar",
          sidebarId: "api",
          position: "left",
          label: "API Spec",
        },
      ],
    },
    footer: {
      style: "dark",
      links: [],
      copyright: `Copyright © ${new Date().getFullYear()} Snowfall Limited.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
    docs: {
      sidebar: {
        hideable: true,
      },
    },
  },
};

export default config;
