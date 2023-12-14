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
    unknown: "Unknown",
  },
  actions: {
    logout: "Logout",
    continue: "Continue",
    cancel: "Cancel",
    reportAnIssue: "Report an issue",
    click: "Click",
    goToLogin: "Go to login",
    search: "Search",
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
    help: {
      title: "Help",
      pages: {
        privacyPolicy: {
          title: "Privacy Policy",
          content: [
            {
              type: "p",
              html: "We believe in protecting the end customer’s privacy. Please see our privacy policy at (insert hyperlink to Website Privacy Policy) and please make your privacy policy available to the end customer as this will apply to their booking.",
            },
            { type: "h2", html: "Indemnification" },
            {
              type: "p",
              html: "You agree to defend us, and/or our respective suppliers and any of their officers, directors, employees, and agents from and against any claims, causes of action, demands, recoveries, losses, damages, fines, penalties or other costs or expenses of any kind or nature including but not limited to reasonable legal and accounting fees, brought by third parties as a result of:",
            },
            {
              type: "ul",
              items: [
                "- Your breach of this Agreement or the documents referenced herein;",
                "- Your violation of any law or the rights of a third party; or",
                "- Your use of the Booking Hub.",
              ],
            },
            { type: "h2", html: "Currency Converter, Price, and Payment" },
            {
              type: "p",
              html: "Prices for travel services are dynamic and subject to frequent change at any time. Price changes will not affect bookings already submitted, except where there has been an obvious error. We make every effort to ensure that the prices we display are accurate and available. Snowfall accepts no liability for bookings at an incorrect price where the error was (or ought to have been) reasonably apparent at the time of booking, or due to Snowfall’s failure to exercise reasonable care.",
            },
            {
              type: "p",
              html: "The prices displayed through our service may include taxes. Such taxes may include amounts associated with value-added tax, goods and services tax, sales tax, occupancy tax and other taxes of a similar nature.",
            },
            {
              type: "p",
              html: "In certain jurisdictions, where applicable, the end customer may also be responsible for paying local taxes imposed by local tax authorities (such as city taxes or tourist taxes, etc). We will notify You of any local taxes that will be payable by the end customer prior to completion of the booking, where such taxes have been notified to us by the travel provider.",
            },
            {
              type: "p",
              html: "The amount of local taxes can change between the booking date and stay date. If taxes have changed by the date of travel, the end customer may be liable to pay taxes at the higher rate.",
            },
            {
              type: "p",
              html: "Payment is made directly to Snowfall Limited on behalf of the travel provider only.",
            },
            {
              type: "p",
              html: "The travel provider usually requires payment upfront; it may be taken or pre-authorised when the booking is made, and it will usually be non-refundable. Before You make a booking, please note the individual booking terms and conditions that apply.",
            },
            {
              type: "p",
              html: "We may store the end customer’s method of payment details for future transactions if You have obtained their consent to do so.",
            },
            {
              type: "p",
              html: "As mentioned above, You accept the applicable policies as displayed in the booking process. You'll find each travel provider's cancellation policy and any other policies (about age requirements, cards accepted, etc.) in the fine print, and/or in the confirmation email or ticket (if applicable).",
            },
            {
              type: "p",
              html: "As You are making a booking on behalf of anyone else, You accept responsibility for obtaining their permission before providing us with their personal data.",
            },
            { type: "h2", html: "Cancellations and Refunds" },
            {
              type: "p",
              html: "The cancellation fees applied to the booking are subject to the specific policy set by the respective provider. These fees will vary based on the terms and conditions of the provider, and we hold no responsibility for their determination. While we endeavour to provide accurate and timely refund processing, we accept no responsibility for the actions or policies of the third-party provider. Any disputes or concerns related to cancellations, refunds, or associated fees should be addressed directly with the individual provider.",
            },
            { type: "h2", html: "Account Termination" },
            {
              type: "p",
              html: "At our sole discretion, we may terminate account holders who are deemed to be repeat infringers. We may also at our sole discretion limit access to the Booking Hub and/or terminate the accounts of any users who infringe any intellectual property rights of others, whether or not there is any repeat infringement.",
            },
            { type: "h2", html: "General" },
            {
              type: "p",
              html: "If any part of this Agreement is found to be invalid, illegal, or unenforceable, the validity, legality and enforceability of the remaining provisions will not in any way be affected or impaired. Our failure or delay in enforcing any provision of this Agreement at any time does not waive our right to enforce the same or any other provision(s) hereof in the future. This Agreement (and any other terms and conditions referenced herein) constitutes the entire agreement between You and us with respect to the Booking Hub and it supersedes all prior or contemporaneous communications and proposals, whether electronic, oral, or written, between the end customer and us with respect to the Booking Hub.",
            },
            {
              type: "p",
              html: "Access to this Booking Hub is conditional on Your agreement that all information contained in it and all matters that arise between You and us will be governed by the laws of England and Wales. It is also conditional on Your agreement that any dispute that arises between You and us will be subject to the exclusive jurisdiction of the Courts of England and Wales.",
            },
            {
              type: "p",
              html: "Any rights not expressly granted herein are reserved.",
            },
            { type: "h2", html: "Contact" },
            {
              type: "p",
              html: 'All comments, queries and requests relating to our use of Your information should be addressed to <a href="mailto:legal@snowfalltravel.com">legal@snowfalltravel.com</a>',
            },
          ] satisfies (
            | { type: "p"; html: string }
            | { type: "h2"; html: string }
            | { type: "ul"; items: string[] }
          )[],
        },
      },
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
