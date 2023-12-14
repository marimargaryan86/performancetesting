import type { LocaleData } from "i18n";

export default {
  roles: {
    "reseller-admin": "Återförsäljare - administratör",
    "reseller-user": "Återförsäljare",
    "snowfall-admin": "Snowfall - administratör",
    "snowfall-user": "Snowfall",
  },
  words: {
    help: "Hjälp",
  },
  actions: {
    logout: "Logga ut",
  },
  sentences: {
    reportAnIssue: "Felrapportera",
  },
  pages: {
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
} satisfies LocaleData;
