import type { UserRole } from "integration/ory/schemas/authentication";

export default {
  title: "Junction Hub",
  roles: {
    "reseller-admin": "Reseller admin",
    "reseller-user": "Reseller user",
    "snowfall-admin": "Snowfall admin",
    "snowfall-user": "Snowfall user",
  } satisfies Record<UserRole, string>,
  words: {
    yes: "Yes",
    no: "No",
    help: "Help",
  },
  actions: {
    logout: "Logout",
    continue: "Continue",
    cancel: "Cancel",
    reportAnIssue: "Report an issue",
    click: "Click",
    goToLogin: "Go to login",
  },
  sentences: {
    priceChange: "Price change",
    priceChangeInfo:
      'We have noticed a price change; the initial price was <strong class="typography body-medium bold">{originalPrice}</strong>, and the new price is <strong class="typography body-medium bold">{newPrice}</strong>. Do you wish to continue?',
    areYouSure: "Are you sure?",
    copiedToClipboard: "Copied to clipboard",
  },
  pages: {
    dashboard: {
      title: "Dashboard",
      intro: "<strong>Welcome to</strong><span>Junction Hub</span>",
    },
    account: {
      title: "Account settings",
    },
    knowledgeHub: {
      title: "Knowledge Hub",
    },
    pay: {
      pages: {
        activity: {
          title: "Activity",
        },
        bills: {
          title: "Bills",
        },
      },
    },
    tripManagement: {
      pages: {
        book: {
          title: "Book",
        },
        orders: {
          title: "View orders",
        },
      },
    },
  },
  ory: {
    formGroups: {
      default: "Default",
      password: "Update password",
      oidc: "OIDC",
      profile: "General",
      link: "Link",
      code: "Code",
      totp: "Two-factor authentication",
      // eslint-disable-next-line camelcase
      lookup_secret: "Backup recovery codes",
      webauthn: "Security keys",
    },
  },
};
