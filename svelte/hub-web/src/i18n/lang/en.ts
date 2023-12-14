import type { UserRole } from "integration/ory/schemas/authentication";

export default {
  roles: {
    "reseller-admin": "Reseller admin",
    "reseller-user": "Reseller user",
    "snowfall-admin": "Snowfall admin",
    "snowfall-user": "Snowfall user",
  } satisfies Record<UserRole, string>,
  words: {
    help: "Help",
  },
  actions: {
    logout: "Logout",
  },
  sentences: {
    reportAnIssue: "Report an issue",
  },
  pages: {
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
};
