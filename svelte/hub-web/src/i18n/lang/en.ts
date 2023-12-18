import type { StatusBadgeValue } from "components/ui/status-badge.svelte";
import type { UserRole } from "integration/ory/schemas/authentication";

type ContentElement =
  | { type: "p"; html: string }
  | { type: "h2"; html: string }
  | { type: "ul"; items: string[] };

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
    notAvailable: "N/A",
  },
  actions: {
    logout: "Logout",
    continue: "Continue",
    cancel: "Cancel",
    reportAnIssue: "Report an issue",
    click: "Click",
    goToLogin: "Go to login",
    search: "Search",
    newOrder: "New Order",
    download: "Download",
  },
  sentences: {
    priceChange: "Price change",
    priceChangeInfo:
      'We have noticed a price change; the initial price was <strong class="typography body-medium bold">{originalPrice}</strong>, and the new price is <strong class="typography body-medium bold">{newPrice}</strong>. Do you wish to continue?',
    areYouSure: "Are you sure?",
    copiedToClipboard: "Copied to clipboard",
  },
  tableHeaders: {
    orderId: "Order ID",
    createdDate: "Created Date",
    updatedDate: "Updated Date",
    owedToUs: "Owed to us",
    reconciledQuestion: "Reconciled?",
    orderReference: "Order Reference",
    tickets: "Ticket(s)",
    departureDate: "Departure Date",
    passengers: "Passengers",
    totalPrice: "Total Price",
    bookingStatus: "Booking Status",
    cancellationStatus: "Cancellation Status",
    refundStatus: "Refund Status",
  },
  statuses: {
    confirmed: "Confirmed",
    "no-refund": "No Refund",
    "not-ticketed": "Not Ticketed",
    "refund-due": "Refund Due",
    "refund-failed": "Refund Failed",
    "refund-issued": "Refund Issued",
    cancelled: "Cancelled",
    completed: "Completed",
    deleted: "Deleted",
    error: "Error",
    executed: "Executed",
    failed: "Failed",
    mixed: "Mixed",
    pending: "Pending",
    rejected: "Rejected",
    submitted: "Submitted",
    succeeded: "Succeeded",
    unknown: "Unknown",
    unspecified: "Unspecified",
  } satisfies Record<StatusBadgeValue, string>,
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
          ] satisfies ContentElement[],
        },
        termsAndConditions: {
          title: "Terms and Conditions",
          content: [
            { type: "h2", html: "Booking Terms of Use" },
            {
              type: "p",
              html: "These Booking Terms (the “Terms”) apply to bookings made via the Junction online client portal (the “Booking Hub”) which is owned and operated by Snowfall Limited, a company registered in England (Company no: 12356236, 10-12 East Parade, Leeds, West Yorkshire, LS1 2BH). The Booking Hub is provided to assist in making reservations and/or otherwise transacting with travel providers. This service is offered to You, the agent, subject to Your acceptance, without modification, of all the terms, conditions, and notices collectively set out in these Terms, the Junction Client Booking Hub Terms of Use, and the Snowfall Travel Website Terms of Use, and the Privacy Policy (collectively, the “Agreement”). In making a booking through the Booking Hub, You agree to be bound by this Agreement. These Terms supplement the terms of any agreement that You may have with us, but solely with respect to the making of bookings as facilitated through the Booking Hub. In the event of a direct conflict between these Terms and any other agreement You may have with us, these Terms will control the details of the booking. The term “You” refers to the customer service agent making the booking on behalf of the end customer.",
            },
            {
              type: "p",
              html: "Please read the Agreement carefully. We reserve the right at any time, at our sole discretion, to change or otherwise modify the Agreement without prior notice.",
            },
            { type: "h2", html: "Conditions of Use" },
            {
              type: "p",
              html: "As a condition of Your use of the Booking Hub, You warrant that (i) You are at least 18 years of age; (ii) You possess the legal authority to create a binding legal obligation; (iii) You will use the Booking Hub to book only in accordance with any applicable terms and conditions and policies; (iv) You will only use the Booking Hub to make reservations for another person for whom You are legally authorised to act; (v) You will inform such other persons about the terms and conditions that apply to the reservations You have made on their behalf, including all rules and restrictions applicable thereto; (vi) all information supplied by You on the Booking Hub is true, accurate, current and complete, and (vii) if You have an account, You will safeguard Your account information and will supervise and be completely responsible for any use of Your account by You and anyone other than You. We retain the right at our sole discretion to deny access to anyone to the Booking Hub and the services we offer, at any time and for any reason, including, but not limited to, for violation of these terms and conditions.",
            },
            { type: "h2", html: "Prohibited Activities" },
            {
              type: "p",
              html: "The content and information on the Booking Hub (including, but not limited to, price and availability of travel services), as well as the infrastructure used to provide such content and information, is proprietary to us or our suppliers and providers. You agree not to: make any speculative, false, or fraudulent reservation or any reservation in anticipation of demand; access, monitor or copy any content or information of this Website using any robot, spider, scraper or other automated means or any manual process for any purpose without our express written permission; violate the restrictions in any robot exclusion headers on this Website or bypass or circumvent other measures employed to prevent or limit access to this Website; take any action that imposes, or may impose, in our discretion, an unreasonable or disproportionately large load on our infrastructure; deep-link to any portion of this Website (including, without limitation, the purchase path for any travel services) for any purpose without our express written permission; or “frame”, “mirror” or otherwise incorporate any part of the Booking Hub into any other Website without our prior written authorisation.",
            },
            { type: "h2", html: "Fraud" },
            {
              type: "p",
              html: "If an account shows repeated signs of fraud, abuse, association with a government-sanctioned person or entity, or other suspicious activity, we may request extra information from You.",
            },
            {
              type: "p",
              html: "Following review of that information and if we reasonably conclude that a booking or account is associated with suspicious activity, we may:",
            },
            {
              type: "ul",
              items: [
                "- Cancel any bookings associated with Your name, email address or account;",
                "- Close any associated accounts;",
                "- Take legal action, including to seek to hold You liable for any loss.",
              ],
            },
            {
              type: "p",
              html: "Please contact us about the cancellation of a booking or closing of an account if You believe a mistake has occurred.",
            },
            { type: "h2", html: "Making Travel Bookings" },
            {
              type: "p",
              html: "Any travel services which You can find and/or book via the Booking Hub are provided by third-party suppliers. We are not responsible and have no liability to You or the end customer in respect of such bookings. The identity of the relevant travel provider and the terms and conditions that govern and apply to the booking will be notified to You at the time of booking and You should ensure that You read and fully understand them before completing the booking, and communicate them to the end customer. You acknowledge that breaching the terms and conditions notified to You by the travel provider could result in the cancellation of tickets, cancellation of hotel reservations etc. and impose additional charges for the end customer.",
            },
            { type: "h2", html: "Limitations and Exclusions of Liability" },
            {
              type: "p",
              html: "In operating the Booking Hub, we merely facilitate bookings with third parties and bear no responsibility for providing any travel options displayed on the Booking Hub or for any arrangements made with any third party on behalf of the end customer as a result of the use of the Booking Hub. Any issues and/or differences that may arise with booking(s) must be resolved with the relevant travel provider. To the maximum extent permitted by law, we do not accept any liability for any inaccuracies or omissions in the content displayed on or via the Booking Hub or any Act of God, accident, delay or any special, exemplary, punitive, indirect, incidental or consequential loss or damage of any kind (including, without limitation, lost profits or lost savings), whether based in contract, tort (including negligence), strict liability or otherwise, incurred by You or the end customer arising out of or in connection with Your access to, use of, or inability to access or use of the Booking Hub or any content contained provided therein.",
            },
            {
              type: "p",
              html: "Our maximum aggregate liability to You and/or the end customer arising out of or in connection with these terms and conditions or Your access to, use of, or inability to access or use, the Booking Hub shall be limited to the maximum extent permitted by law. The present terms and conditions provide the full extent of our obligations and liabilities in respect of the Booking Hub. Nothing in these Terms shall limit or exclude (a) our liability in respect of death or personal injury caused by our negligence or for our fraud or fraudulent misrepresentation; (b) any other liability that cannot be excluded by law; or (c) the end customer’s statutory rights.",
            },
          ] satisfies ContentElement[],
        },
        customerService: {
          title: "Customer Service",
          content: [
            {
              type: "p",
              html: "Contact us with your request for specialised assistance",
            },
            {
              type: "p",
              html: '<a href="mailto:support@snowfalltravel.com?subject=GG%20-%20">support@snowfalltravel.com</a>',
            },
          ] satisfies ContentElement[],
        },
        conditionsOfCarriage: {
          title: "Conditions of Carriage",
          content: [
            {
              type: "p",
              html: "Train operator conditions. Your booking of train tickets/ rail passes is subject to the transportation terms and conditions of one or more rail operators. Please select and view the carrier conditions applicable to your trip.",
            },
          ] satisfies ContentElement[],
        },
      },
    },
    knowledgeHub: {
      title: "Knowledge Hub",
      videos: {
        title: "Video Tutorials",
        description:
          "Get to know Junction Hub in just a few minutes with our quick video tutorials.",
        items: [
          {
            title: "Search for a trip",
            description: "Find out how to search for rail trips in Junction Hub.",
            id: "qMTv6kNAIEU",
            lengthS: 60,
          },
          {
            title: "Select an offer",
            description:
              "Find out how to select an offer for your customer’s booking in Junction Hub.",
            id: "JdfyhZU3kQg",
            lengthS: 69,
          },
          {
            title: "Add passenger details",
            description: "Find out how to add passenger details to a rail booking in Junction Hub.",
            id: "Zcidy7py-xY",
            lengthS: 37,
          },
          {
            title: "Total to pay, add commission & view fare rules",
            description:
              "Find out how to view booking balances, fare rules and add fees and commissions.",
            id: "pB05rIT8N3I",
            lengthS: 63,
          },
          {
            title: "Confirm a booking",
            description:
              "Find out how to make a payment using your agency card and confirm a booking in Junction Hub.",
            id: "OQMqh6fCczo",
            lengthS: 69,
          },
          {
            title: "Check order status",
            description:
              "Find out how to view all of your existing orders, check their status and download your customers’ tickets in Junction Hub.",
            id: "2ZHcdPvcJ-U",
            lengthS: 47,
          },
        ],
      },
      faq: {
        title: "Frequently Asked Questions",
        items: [
          {
            question: "What train operators are available through Junction Hub?",
            answer:
              "Junction Hub gives you access to a host of rail journeys across Europe, aboard operators such as Eurostar, SNCF, Thalys, Deutsche Bahn and more.",
          },
          {
            question: "Can I view and compare different journey times and prices in one place?",
            answer:
              "By searching in Junction Hub, you can easily see all of the available departures for your chosen travel dates, and compare the different fare types and prices on your customers’ behalf.",
          },
          {
            question: "What payment options are accepted?",
            answer: "Currently all booking payments are made using your agency credit card.",
          },
          {
            question: "How do I cancel bookings in Junction Hub?",
            answer:
              "To cancel a booking, you will need to make a cancellation request. Take a look at our user guide, or watch our short video tutorial, for more information on how to cancel a booking in Junction Hub.",
          },
          {
            question: "How do I access customers’ train tickets?",
            answer:
              "Navigate to the “Orders” tab, where you can view all existing orders and their status. To download your customers’ tickets, select their order and click on the “Download ticket” link.",
          },
          {
            question: "How do I contact customer support?",
            answer:
              "The Snowfall support team is on hand to help if you have any issues. Simply email support@snowfalltravel.com.",
          },
        ],
      },
    },
    pay: {
      title: "Pay",
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
      title: "Trip Management",
      pages: {
        book: {
          title: "Book",
        },
        orders: {
          title: "Orders",
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
