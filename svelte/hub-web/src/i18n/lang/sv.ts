import type { LocaleData } from "i18n";

export default {
  title: "Junction Hub",
  roles: {
    "reseller-admin": "Återförsäljare - administratör",
    "reseller-user": "Återförsäljare",
    "snowfall-admin": "Snowfall - administratör",
    "snowfall-user": "Snowfall",
  },
  words: {
    yes: "Ja",
    no: "Nej",
    help: "Hjälp",
  },
  actions: {
    logout: "Logga ut",
    continue: "Fortsätt",
    cancel: "Avbryt",
    reportAnIssue: "Felrapportera",
    click: "Klicka",
    goToLogin: "Gå till login",
  },
  sentences: {
    priceChange: "Prisändring",
    priceChangeInfo:
      'Vi har upptäckt en prisändring; ursprungspriset var <strong class="typography body-medium bold">{originalPrice}</strong> och det nya priset är <strong class="typography body-medium bold">{newPrice}</strong>. Vill du fortsätta?',
    areYouSure: "Är du säker?",
    copiedToClipboard: "Kopierad till urklipp",
  },
  pages: {
    dashboard: {
      title: "Instrumentbräda",
      intro: "<strong>Välkommen till</strong><span>Junction Hub</span>",
    },
    account: {
      title: "Kontoinställningar",
    },
    knowledgeHub: {
      title: "Kunskapshub",
    },
    pay: {
      pages: {
        activity: {
          title: "Aktivitet",
        },
        bills: {
          title: "Räkningar",
        },
      },
    },
    tripManagement: {
      pages: {
        book: {
          title: "Boka",
        },
        orders: {
          title: "Visa ordrar",
        },
      },
    },
  },
  ory: {
    formGroups: {
      default: "Standard",
      password: "Uppdatera lösenord",
      oidc: "OIDC",
      profile: "Allmänt",
      link: "Länk",
      code: "Kod",
      totp: "Tvåfaktorsautentisering",
      // eslint-disable-next-line camelcase
      lookup_secret: "Återställningskoder",
      webauthn: "Säkerhetsnycklar",
    },
  },
} satisfies LocaleData;
