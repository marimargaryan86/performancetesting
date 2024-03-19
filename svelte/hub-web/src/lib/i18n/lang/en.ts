/* eslint-disable camelcase */
import type { StatusBadgeValue } from "$lib/models/status-badge";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";
import type * as OrySchemas from "~/integration/ory/schemas";
import type { PassengerType } from "$lib/models/passenger";
import type * as CommonSchemas from "~/integration/common/schemas";
import type { TripType } from "$lib/components/pages/trip-management/book/search/trip-search-data";
import type { OfferSortOption } from "$lib/sorting/offer";

export default {
  title: "Junction Hub",
  roles: {
    "reseller-admin": "Reseller admin",
    "reseller-user": "Reseller user",
    "snowfall-admin": "Snowfall admin",
    "snowfall-user": "Snowfall user",
  } satisfies Record<OrySchemas.UserRole, string>,
  words: {
    yes: "Yes",
    no: "No",
    help: "Help",
    unknown: "Unknown",
    notAvailable: "N/A",
    subAccounts: "Sub accounts",
    balances: "Balances",
    from: "From",
    to: "To",
    depart: "Depart",
    passenger_one: "Passenger",
    passenger_other: "Passengers",
    fareRules: "Fare rules",
    stop_zero: "Direct",
    stop_one: "Stop",
    stop_other: "Stops",
    stopCounter_zero: "$t(words.stop_zero)",
    stopCounter: "{{count}} $t(words.stop, lowercase)",
    departureTime: "Departure time",
    departure: "Departure",
    arrival: "Arrival",
    journeyDuration: "Journey duration",
    railwayOperators: "Railway operators",
    alternativeFares: "Alternative fares",
    selected: "Selected",
    dateRange: "Date Range",
    none: "None",
    title: "Title",
    firstName: "First name",
    lastName: "Last name",
    birthdayDate: "Birthday",
    gender: "Gender",
    documentType: "Document type",
    documentNumber: "Document number",
    expiryDate: "Expiration date",
    issueDate: "Issue date",
    issuingCountry: "Issuing country",
    nationality: "Nationality",
    residenceCountryCode: "Residence country code",
    summary: "Summary",
    fareBrand_one: "Fare Brand",
    fareBrand_other: "Fare Brands",
    itinerary: "Itinerary",
    fee_one: "Fee",
    fee_other: "Fees",
    serviceFee: "Service fee",
    agencyMarkup: "Agency mark-up",
    paymentMethod: "Payment method",
    contactInformation: "Contact information",
    countryCode: "Country code",
    phoneNumber: "Phone number",
    email: "Email",
    addressLine1: "Address line 1",
    addressLine2: "Address line 2",
    city: "City",
    country: "Country",
    postcode: "Postcode",
    error: "Error",
    success: "Success",
    warning: "Warning",
    status: "Status",
    passengerDetails: "Passenger details",
    itineraryDetails: "Itinerary details",
    tripDuration: "Trip duration",
    orderReference: "Order reference",
    cancellation: "Cancellation",
    reservationNumber: "Reservation number",
    orderDetails: "Order details",
    booking: "Booking",
    bookingStatus: "Booking status",
    cancellationStatus: "Cancellation status",
    refund: "Refund",
    total: "Total",
    transactionInfo: "Transaction info",
    transactionType: "Transaction type",
    paymentType: "Payment type",
    provider: "Provider",
    reseller: "Reseller",
    markup: "Markup",
    refundPosition: "Refund position",
    withoutAmounts: "Without amounts",
    withAmounts: "With amounts",
    amount: "Amount",
    refundReference: "Refund reference",
    bookTrip: "Book a Trip",
    manageTrip: "Manage a Trip",
    passengerNameRecord: "Reference number",
    optional: "Optional",
    inbound: "Inbound",
    outbound: "Outbound",
    admin: "Admin",
    user: "User",
    earlier: "Earlier",
    later: "Later",
    ok: "Ok",
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
    addBalance: "Add Balance",
    addBalances: "Add Balances",
    add: "Add",
    addDate: "Add date",
    returnToBookings: "Return to bookings",
    sortBy: "Sort by",
    selectAll: "Select all",
    clearAll: "Clear all",
    bookNow: "Book now",
    viewFareRules: "View fare rules",
    clear: "Clear",
    select: "Select",
    enterFirstName: "Enter first name",
    enterLastName: "Enter last name",
    enterDocumentNumber: "Enter document number",
    enterIssuingCountry: "Enter issuing country",
    enterNationality: "Enter nationality",
    enterResidenceCountryCode: "Enter residence country code",
    enterAmount: "Enter amount",
    selectFeeType: "Select fee type",
    tryAgain: "Try again",
    enterPhoneNumber: "Enter phone number",
    enterEmail: "Enter email",
    enterAddressLine1: "Enter address line 1",
    enterAddressLine2: "Enter address line 2",
    enterCity: "Enter city",
    selectCountry: "Select country",
    enterPostcode: "Enter postcode",
    next: "Next",
    previous: "Previous",
    book: "Book",
    downloadTickets: "Download tickets",
    cancelBooking: "Cancel booking",
    goBack: "Go back",
    view: "View",
    cancelRequest: "Cancel",
    refundWithNoAmount: "Refund with no amount",
    calculateRefundPosition: "Calculate refund position",
    issueRefund: "Issue refund",
    enterRefundReference: "Enter refund reference",
    bookTrip: "Book Trip",
    findTrip: "Find Trip",
    modifySearch: "Modify Search",
    addUser: "Add User",
    save: "Save",
    change: "Change",
    confirmSelection: "Confirm selection",
    deactivate: "Deactivate",
    discard: "Discard",
  },
  sentences: {
    priceChange: "Price change",
    priceChangeInfo:
      'We have noticed a price change; the initial price was <strong typography="body-medium" weight="bold">{{originalPrice}}</strong>, and the new price is <strong typography="body-medium" weight="bold">{{newPrice}}</strong>. Do you wish to continue?' satisfies `${string}{{originalPrice}}${string}{{newPrice}}${string}`,
    areYouSure: "Are you sure?",
    copiedToClipboard: "Copied to clipboard",
    noBalancesFound: "No balances found",
    findABalance: "Find a balance",
    cityOrStation: "City or Station",
    noTripsMatchesTheFilterCriteria: "No trips matches the filter criteria",
    noTripsFound: "No trips found",
    timeRemaining: "Time remaining",
    priceQuoteTimeRemainingInfo:
      '{{timeLeft}} mins to <strong weight="bold">complete</strong> your booking' satisfies `${string}{{timeLeft}}${string}`,
    offerSearchTimeRemainingInfo:
      '{{timeLeft}} mins to <strong weight="bold">select</strong> your offer' satisfies `${string}{{timeLeft}}${string}`,
    startingAt: "From",
    loadingTripDetails: "Loading trip details...",
    thisPriceIsForAllPassengers: "This price is for all passengers",
    totalToPay: "Total to pay",
    fareRulesInfo: [
      {
        type: "text",
        value:
          "Fares are not guaranteed until full payment is received and tickets are issued. See all the applicable",
      },
      { type: "fareRulesButton", value: "Fare Rules" },
      { type: "text", value: "and" },
      { type: "fareRulesButton", value: "Baggage Information" },
    ] satisfies { type: "text" | "fareRulesButton"; value: string }[],
    totalToCollect: "Total to collect",
    paymentDeclined: "Payment declined",
    anUnexpectedErrorOccurred: "An unexpected error occured",
    paymentInfo: [
      { type: "text", value: "By booking your ticket you accept Snowfall’s" },
      { type: "toc", value: "T&C" },
      { type: "text", value: "the" },
      { type: "coc", value: "carrier’s conditions of carriage" },
      { type: "text", value: "and our" },
      { type: "privacy", value: "privacy policy" },
    ] satisfies { type: "text" | "toc" | "coc" | "privacy"; value: string }[],
    oopsSomethingWentWrong: "Oops, something went wrong :(",
    theOrderWasCreatedSuccessfully: "The order was created successfully",
    theOrderWasCreatedWithErrors: "The order was created with errors",
    theOrderIsInAPendingState: "The order is in a pending state",
    yourOrderHasBeenCreated: "Your order has been created",
    totalPaid: "Total paid",
    newSearch: "New search",
    youAreCancellingThisBooking: "You are cancelling this booking",
    rulesAndFees: "Rules and Fees",
    pleaseReviewTheFollowingRules:
      "Please review the following rules before cancelling, including any applicable fees.",
    doYouWishToContinue: "Do you wish to continue?",
    thisCannotBeUndone: "This cannot be undone.",
    cancellationRequestReceived: "Cancellation request received",
    cancellationRequestFailed: "Cancellation request failed",
    cancellationRequestInfo:
      "We have received your cancellation request. A member of our support team will contact you shortly with further details.",
    contactSnowfallSupport: "You can contact Snowfall support on",
    transactionNotFound: "Transaction not found",
    toUs: "To us",
    payerCurrency: "Payer currency",
    toReseller: "To reseller",
    createRefundWithoutAmounts: "Are you sure you want to create a refund with no amounts?",
    resellerHowMuchWeGiveBack: "Reseller - how much we give back",
    providerHowMuchWeGetBack: "Provider - how much we get back",
    refundReferenceInfo:
      "The refund has to be handled manually, please do so and enter the refund reference above",
    bookTrip:
      "Search, book and pay for multimodal content from thousands of providers and operators – in a single booking.",
    manageTrip:
      "Retrieve your trip to change or cancel bookings, view/print itinerary and much more.",
    passengerNameRecordPlaceholder: "For example: 9A2FDF56",
    passengerLastNamePlaceholder: "As on your booking confirmation",
    passengerNameRecordError: "Your reference is a sequence of eight letters and/or numbers.",
    noTripsFoundMessage:
      "Please ensure you have entered the correct reference number.\nPlease try again or contact support.",
    adminRoleDescription:
      "View and manage any orders made within the agency. Manage reseller & user settings.",
    userRoleDescription: "View and manage your own orders for a personalized experience.",
    totalAmount: "Total amount",
    fetchingSelection: "Fetching selection",
    previousSelectedOutboundUnavailable:
      "Your previously selected outbound trip is no longer available",
    previousSelectedInboundUnavailable:
      "Your previously selected inbound trip is no longer available",
    deleteUser: "Are you sure you want to delete this user?",
    discardChangesTitle: "Discard changes?",
    discardChangesBody: "You have unsaved changes. Are you sure you want to discard your changes?",
  },
  tableHeaders: {
    id: "ID",
    orderId: "Order ID",
    createdDate: "Created Date",
    updatedDate: "Updated Date",
    owedToUs: "Owed to us",
    reconciledQuestion: "Reconciled?",
    orderReference: "Order Reference",
    ticket: "Ticket",
    tickets: "Ticket(s)",
    departureDate: "Departure Date",
    passengers: "Passengers",
    totalPrice: "Total Price",
    bookingStatus: "Booking Status",
    cancellationStatus: "Cancellation Status",
    refundStatus: "Refund Status",
    transactionType: "Transaction type",
    paymentType: "Payment type",
    payer: "Payer",
    beneficiary: "Beneficiary",
    whatWeOwe: "What we owe",
    salesProfit: "Sales Profit",
    reference: "Reference",
    settlement: "Settlement",
    from: "From",
    to: "To",
    quoteRate: "Quote Rate",
    transactionRate: "Transaction Rate",
    fxDelta: "FX Delta",
    fxBuffer: "FX Buffer",
    status: "Status",
    booking: "Booking",
    origin: "Origin",
    destination: "Destination",
  },
  transportTypes: {
    rail: "Train",
    car: "Car Rental",
  } satisfies Record<Exclude<CommonSchemas.TransportType, "unspecified" | "air">, string>,
  gender: {
    female: "Female",
    male: "Male",
    unspecified: "Unspecified",
  } satisfies Record<CommonSchemas.Gender, string>,
  documentTypes: {
    passport: "Passport",
  } satisfies Record<CommonSchemas.TravelerDocumentType, string>,
  passengerTitle: {
    miss: "Miss",
    mr: "Mr",
    mrs: "Mrs",
    ms: "Ms",
    unspecified: "Unspecified",
  } satisfies Record<CommonSchemas.PassengerTitle, string>,
  passengerTypes: {
    adult_one: "Adult",
    adult_other: "Adults",
    child_one: "Child",
    child_other: "Children",
    senior_one: "Senior",
    senior_other: "Seniors",
    youth_one: "Youth",
    youth_other: "Youths",
  } satisfies Record<`${PassengerType}_${"one" | "other"}`, string>,
  tripTypes: {
    "one-way": "One way",
    "round-trip": "Round trip",
  } satisfies Record<TripType, string>,
  types: {
    "bank-transfer": "Bank Transfer",
    card: "Card",
    invoice: "Invoice",
    transactional: "Transactional",
    unspecified: "Unspecified",
  } satisfies Record<HubSchemas.PaymentType | HubSchemas.PaymentMethod, string>,
  priceBreakdownTypes: {
    "base-fare": "Base fare",
    "company-mark-up": "Company mark-up",
    "reseller-mark-up": "Reseller mark-up",
    "service-mark-up": "Service mark-up",
    tax: "Taxes",
  } satisfies Record<CommonSchemas.PriceBreakdownType, string>,
  sortOptions: {
    "earliest-arrival": "Earliest arrival",
    "earliest-departure": "Earliest departure",
    "lowest-price": "Lowest price",
    fastest: "Fastest",
  } satisfies Record<OfferSortOption, string>,
  statuses: {
    active: "Active",
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
    adminControls: {
      title: "Admin Controls",
      pages: {
        users: {
          title: "Users",
          pages: {
            create: {
              title: "Add User",
              subTitle: "Create a new user",
            },
            update: {
              title: "Update User",
              subTitle: "Update user information",
            },
            delete: {
              title: "Delete User",
              subTitle: "Delete a user",
            },
          },
        },
      },
    },
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
          content: `
<p>We believe in protecting the end customer’s privacy. Please see our <a href="https://snowfalltravel.com/privacy-policy">privacy policy</a> and please make your privacy policy available to the end customer as this will apply to their booking.</p>
<h2 typography="body-large" weight="bold">Indemnification</h2>
<p>You agree to defend us, and/or our respective suppliers and any of their officers, directors, employees, and agents from and against any claims, causes of action, demands, recoveries, losses, damages, fines, penalties or other costs or expenses of any kind or nature including but not limited to reasonable legal and accounting fees, brought by third parties as a result of:</p>
<ul>
  <li>- Your breach of this Agreement or the documents referenced herein;</li>
  <li>- Your violation of any law or the rights of a third party; or</li>
  <li>- Your use of the Booking Hub.</li>
</ul>
<h2 typography="body-large" weight="bold">Currency Converter, Price, and Payment</h2>
<p>Prices for travel services are dynamic and subject to frequent change at any time. Price changes will not affect bookings already submitted, except where there has been an obvious error. We make every effort to ensure that the prices we display are accurate and available. Snowfall accepts no liability for bookings at an incorrect price where the error was (or ought to have been) reasonably apparent at the time of booking, or due to Snowfall’s failure to exercise reasonable care.</p>
<p>The prices displayed through our service may include taxes. Such taxes may include amounts associated with value-added tax, goods and services tax, sales tax, occupancy tax and other taxes of a similar nature.</p>
<p>In certain jurisdictions, where applicable, the end customer may also be responsible for paying local taxes imposed by local tax authorities (such as city taxes or tourist taxes, etc). We will notify You of any local taxes that will be payable by the end customer prior to completion of the booking, where such taxes have been notified to us by the travel provider.</p>
<p>The amount of local taxes can change between the booking date and stay date. If taxes have changed by the date of travel, the end customer may be liable to pay taxes at the higher rate.</p>
<p>Payment is made directly to Snowfall Limited on behalf of the travel provider only.</p>
<p>The travel provider usually requires payment upfront; it may be taken or pre-authorised when the booking is made, and it will usually be non-refundable. Before You make a booking, please note the individual booking terms and conditions that apply.</p>
<p>We may store the end customer’s method of payment details for future transactions if You have obtained their consent to do so.</p>
<p>As mentioned above, You accept the applicable policies as displayed in the booking process. You'll find each travel provider's cancellation policy and any other policies (about age requirements, cards accepted, etc.) in the fine print, and/or in the confirmation email or ticket (if applicable).</p>
<p>As You are making a booking on behalf of anyone else, You accept responsibility for obtaining their permission before providing us with their personal data.</p>
<h2 typography="body-large" weight="bold">Cancellations and Refunds</h2>
<p>The cancellation fees applied to the booking are subject to the specific policy set by the respective provider. These fees will vary based on the terms and conditions of the provider, and we hold no responsibility for their determination. While we endeavour to provide accurate and timely refund processing, we accept no responsibility for the actions or policies of the third-party provider. Any disputes or concerns related to cancellations, refunds, or associated fees should be addressed directly with the individual provider.</p>
<h2 typography="body-large" weight="bold">Account Termination</h2>
<p>At our sole discretion, we may terminate account holders who are deemed to be repeat infringers. We may also at our sole discretion limit access to the Booking Hub and/or terminate the accounts of any users who infringe any intellectual property rights of others, whether or not there is any repeat infringement.</p>
<h2 typography="body-large" weight="bold">General</h2>
<p>If any part of this Agreement is found to be invalid, illegal, or unenforceable, the validity, legality and enforceability of the remaining provisions will not in any way be affected or impaired. Our failure or delay in enforcing any provision of this Agreement at any time does not waive our right to enforce the same or any other provision(s) hereof in the future. This Agreement (and any other terms and conditions referenced herein) constitutes the entire agreement between You and us with respect to the Booking Hub and it supersedes all prior or contemporaneous communications and proposals, whether electronic, oral, or written, between the end customer and us with respect to the Booking Hub.</p>
<p>Access to this Booking Hub is conditional on Your agreement that all information contained in it and all matters that arise between You and us will be governed by the laws of England and Wales. It is also conditional on Your agreement that any dispute that arises between You and us will be subject to the exclusive jurisdiction of the Courts of England and Wales.</p>
<p>Any rights not expressly granted herein are reserved.</p>
<h2 typography="body-large" weight="bold">Contact</h2>
<p>All comments, queries and requests relating to our use of Your information should be addressed to <a href="mailto:legal@snowfalltravel.com">legal@snowfalltravel.com</a></p>`,
        },
        termsAndConditions: {
          title: "Terms and Conditions",
          content: `
<h2 typography="body-large" weight="bold">Booking Terms of Use</h2>
<p>These Booking Terms (the “Terms”) apply to bookings made via the Junction online client portal (the “Booking Hub”) which is owned and operated by Snowfall Limited, a company registered in England (Company no: 12356236, 10-12 East Parade, Leeds, West Yorkshire, LS1 2BH). The Booking Hub is provided to assist in making reservations and/or otherwise transacting with travel providers. This service is offered to You, the agent, subject to Your acceptance, without modification, of all the terms, conditions, and notices collectively set out in these Terms, the Junction Client Booking Hub Terms of Use, and the Snowfall Travel Website Terms of Use, and the Privacy Policy (collectively, the “Agreement”). In making a booking through the Booking Hub, You agree to be bound by this Agreement. These Terms supplement the terms of any agreement that You may have with us, but solely with respect to the making of bookings as facilitated through the Booking Hub. In the event of a direct conflict between these Terms and any other agreement You may have with us, these Terms will control the details of the booking. The term “You” refers to the customer service agent making the booking on behalf of the end customer.</p>
<p>Please read the Agreement carefully. We reserve the right at any time, at our sole discretion, to change or otherwise modify the Agreement without prior notice.</p>
<h2 typography="body-large" weight="bold">Conditions of Use</h2>
<p>As a condition of Your use of the Booking Hub, You warrant that (i) You are at least 18 years of age; (ii) You possess the legal authority to create a binding legal obligation; (iii) You will use the Booking Hub to book only in accordance with any applicable terms and conditions and policies; (iv) You will only use the Booking Hub to make reservations for another person for whom You are legally authorised to act; (v) You will inform such other persons about the terms and conditions that apply to the reservations You have made on their behalf, including all rules and restrictions applicable thereto; (vi) all information supplied by You on the Booking Hub is true, accurate, current and complete, and (vii) if You have an account, You will safeguard Your account information and will supervise and be completely responsible for any use of Your account by You and anyone other than You. We retain the right at our sole discretion to deny access to anyone to the Booking Hub and the services we offer, at any time and for any reason, including, but not limited to, for violation of these terms and conditions.</p>
<h2 typography="body-large" weight="bold">Prohibited Activities</h2>
<p>The content and information on the Booking Hub (including, but not limited to, price and availability of travel services), as well as the infrastructure used to provide such content and information, is proprietary to us or our suppliers and providers. You agree not to: make any speculative, false, or fraudulent reservation or any reservation in anticipation of demand; access, monitor or copy any content or information of this Website using any robot, spider, scraper or other automated means or any manual process for any purpose without our express written permission; violate the restrictions in any robot exclusion headers on this Website or bypass or circumvent other measures employed to prevent or limit access to this Website; take any action that imposes, or may impose, in our discretion, an unreasonable or disproportionately large load on our infrastructure; deep-link to any portion of this Website (including, without limitation, the purchase path for any travel services) for any purpose without our express written permission; or “frame”, “mirror” or otherwise incorporate any part of the Booking Hub into any other Website without our prior written authorisation.</p>
<h2 typography="body-large" weight="bold">Fraud</h2>
<p>If an account shows repeated signs of fraud, abuse, association with a government-sanctioned person or entity, or other suspicious activity, we may request extra information from You.</p>
<p>Following review of that information and if we reasonably conclude that a booking or account is associated with suspicious activity, we may:</p>
<ul>
  <li>- Cancel any bookings associated with Your name, email address or account;</li>
  <li>- Close any associated accounts;</li>
  <li>- Take legal action, including to seek to hold You liable for any loss.</li>
</ul>
<p>Please contact us about the cancellation of a booking or closing of an account if You believe a mistake has occurred.</p>
<h2 typography="body-large" weight="bold">Making Travel Bookings</h2>
<p>Any travel services which You can find and/or book via the Booking Hub are provided by third-party suppliers. We are not responsible and have no liability to You or the end customer in respect of such bookings. The identity of the relevant travel provider and the terms and conditions that govern and apply to the booking will be notified to You at the time of booking and You should ensure that You read and fully understand them before completing the booking, and communicate them to the end customer. You acknowledge that breaching the terms and conditions notified to You by the travel provider could result in the cancellation of tickets, cancellation of hotel reservations etc. and impose additional charges for the end customer.</p>
<h2 typography="body-large" weight="bold">Limitations and Exclusions of Liability</h2>
<p>In operating the Booking Hub, we merely facilitate bookings with third parties and bear no responsibility for providing any travel options displayed on the Booking Hub or for any arrangements made with any third party on behalf of the end customer as a result of the use of the Booking Hub. Any issues and/or differences that may arise with booking(s) must be resolved with the relevant travel provider. To the maximum extent permitted by law, we do not accept any liability for any inaccuracies or omissions in the content displayed on or via the Booking Hub or any Act of God, accident, delay or any special, exemplary, punitive, indirect, incidental or consequential loss or damage of any kind (including, without limitation, lost profits or lost savings), whether based in contract, tort (including negligence), strict liability or otherwise, incurred by You or the end customer arising out of or in connection with Your access to, use of, or inability to access or use of the Booking Hub or any content contained provided therein.</p>
<p>Our maximum aggregate liability to You and/or the end customer arising out of or in connection with these terms and conditions or Your access to, use of, or inability to access or use, the Booking Hub shall be limited to the maximum extent permitted by law. The present terms and conditions provide the full extent of our obligations and liabilities in respect of the Booking Hub. Nothing in these Terms shall limit or exclude (a) our liability in respect of death or personal injury caused by our negligence or for our fraud or fraudulent misrepresentation; (b) any other liability that cannot be excluded by law; or (c) the end customer’s statutory rights.</p>`,
        },
        customerService: {
          title: "Customer Service",
          content: `
<p>Contact us with your request for specialised assistance</p>
<p><a href="mailto:support@snowfalltravel.com?subject=GG%20-%20">support@snowfalltravel.com</a></p>`,
        },
        conditionsOfCarriage: {
          title: "Conditions of Carriage",
          content: `
<p>Train operator conditions. Your booking of train tickets/ rail passes is subject to the transportation terms and conditions of one or more rail operators. Please select and view the carrier conditions applicable to your trip.</p>`,
        },
      },
    },
    knowledgeHub: {
      title: "Knowledge Hub",
      userManuals: {
        title: "User Manuals",
        description:
          "Find everything you need to access and start using Junction Hub with our helpful user guide.",
        userManual: "Junction Hub - User Manual",
      },
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
        accounts: {
          title: "Accounts",
        },
        activity: {
          title: "Activity",
          pages: {
            transactions: {
              title: "Transactions",
            },
            conversions: {
              title: "FX",
            },
          },
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
          pages: {
            rail: {
              pages: {
                search: {
                  title: "Search",
                  subTitle: "Search for offers",
                },
                select: {
                  title: "Select",
                  subTitle: "Select an offer",
                  outbound: 'Select <strong weight="bold">outbound</strong>',
                  inbound: 'Select <strong weight="bold">inbound</strong>',
                  findingOutbound: "Finding outbound offers...",
                  findingInbound: "Finding inbound offers...",
                },
                payment: {
                  title: "Payment",
                  subTitle: "Payment",
                },
                confirmation: {
                  title: "Confirmation",
                  subTitle: "Confirmation",
                },
              },
            },
            car: {
              pages: {
                search: {
                  title: "Search",
                  subTitle: "Search for Car Rental",
                },
                select: {
                  title: "Select",
                  subTitle: "Select Car",
                },
                payment: {
                  title: "Payment",
                  subTitle: "Payment",
                },
                confirmation: {
                  title: "Confirmation",
                  subTitle: "Confirmation",
                },
              },
            },
          },
        },
        orders: {
          title: "Orders",
          pages: {
            bookings: {
              title: "Bookings",
            },
            details: {
              title: "Details",
            },
          },
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
      lookup_secret: "Backup recovery codes",
      webauthn: "Security keys",
    },
  },
};
