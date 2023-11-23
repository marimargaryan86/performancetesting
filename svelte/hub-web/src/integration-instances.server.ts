import { env } from "$env/dynamic/private";
import junctionMobileApi from "integration/junction-mobile-api/services";
import junctionHubApi from "integration/junction-hub-api/services";
import ory from "integration/ory/services";

const junctionHubCompanyService = new junctionHubApi.CompanyService(env.HUB_API_BASE_URL);

export default {
  junctionMobileApi: {
    places: new junctionMobileApi.PlaceService(env.BOOKING_HUB_API_BASE_URL),
    trips: new junctionMobileApi.TripService(env.BOOKING_HUB_API_BASE_URL),
    offers: new junctionMobileApi.OfferService(env.BOOKING_HUB_API_BASE_URL),
    orders: new junctionMobileApi.OrderService(env.BOOKING_HUB_API_BASE_URL),
    payments: new junctionMobileApi.PaymentService(env.BOOKING_HUB_API_BASE_URL),
    cancellations: new junctionMobileApi.CancellationRequestService(env.BOOKING_HUB_API_BASE_URL),
    simpleOfferSearches: new junctionMobileApi.SimpleOfferSearchService(
      env.BOOKING_HUB_API_BASE_URL,
    ),
  },
  junctionHubApi: {
    accounts: new junctionHubApi.AccountService(env.HUB_API_BASE_URL),
    beneficiaries: new junctionHubApi.BeneficiaryService(env.HUB_API_BASE_URL),
    currencies: new junctionHubApi.CurrencyService(env.HUB_API_BASE_URL),
    conversions: new junctionHubApi.ConversionService(env.HUB_API_BASE_URL),
    companies: junctionHubCompanyService,
    transactions: new junctionHubApi.TransactionService(
      env.HUB_API_BASE_URL,
      junctionHubCompanyService,
    ),
    bookings: new junctionHubApi.BookingService(env.HUB_API_BASE_URL),
    balances: new junctionHubApi.BalanceService(env.HUB_API_BASE_URL),
    bills: new junctionHubApi.BillService(env.HUB_API_BASE_URL),
    journeys: new junctionHubApi.JourneyService(env.HUB_API_BASE_URL),
    orders: new junctionHubApi.OrderService(env.HUB_API_BASE_URL),
    cancellationRequests: new junctionHubApi.CancellationRequestService(env.HUB_API_BASE_URL),
    users: new junctionHubApi.UserService(env.HUB_API_BASE_URL),
    refunds: new junctionHubApi.RefundService(env.HUB_API_BASE_URL),
  },
  ory: {
    loginFlow: new ory.LoginFlowService(env.ORY_BASE_URL),
    auth: new ory.AuthenticationService(env.ORY_BASE_URL),
  },
};
