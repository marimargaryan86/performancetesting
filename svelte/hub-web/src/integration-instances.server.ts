import { env } from "$env/dynamic/private";
import junctionMobileApi from "integration/junction-mobile-api/services";
import junctionHubApi from "integration/junction-hub-api/services";
import common from "integration/common/services";
import ory from "integration/ory/services";

const junctionHubCompanyService = new junctionHubApi.CompanyService(env.HUB_API_BASE_URL);

export default {
  junctionMobileApi: {
    places: new junctionMobileApi.PlaceService(
      env.BOOKING_HUB_API_BASE_URL,
      env.BOOKING_HUB_API_KEY,
    ),
    trips: new junctionMobileApi.TripService(env.BOOKING_HUB_API_BASE_URL, env.BOOKING_HUB_API_KEY),
    offers: new junctionMobileApi.OfferService(
      env.BOOKING_HUB_API_BASE_URL,
      env.BOOKING_HUB_API_KEY,
    ),
    orders: new junctionMobileApi.OrderService(
      env.BOOKING_HUB_API_BASE_URL,
      env.BOOKING_HUB_API_KEY,
    ),
    payments: new junctionMobileApi.PaymentService(
      env.BOOKING_HUB_API_BASE_URL,
      env.BOOKING_HUB_API_KEY,
    ),
    cancellations: new junctionMobileApi.CancellationRequestService(
      env.BOOKING_HUB_API_BASE_URL,
      env.BOOKING_HUB_API_KEY,
    ),
  },
  junctionHubApi: {
    accounts: new junctionHubApi.AccountService(env.HUB_API_BASE_URL),
    beneficiaries: new junctionHubApi.BeneficiaryService(env.HUB_API_BASE_URL),
    currencies: new junctionHubApi.CurrencyService(env.HUB_API_BASE_URL),
    conversions: new junctionHubApi.ConversionService(env.HUB_API_BASE_URL),
    companyService: junctionHubCompanyService,
    transactions: new junctionHubApi.TransactionService(
      env.HUB_API_BASE_URL,
      junctionHubCompanyService,
    ),
    bookings: new junctionHubApi.BookingService(env.HUB_API_BASE_URL),
    balances: new junctionHubApi.BalanceService(env.HUB_API_BASE_URL),
    bills: new junctionHubApi.BillService(env.HUB_API_BASE_URL),
  },
  common: {
    countries: new common.CountryService(),
  },
  ory: new ory.OryService(env.ORY_BASE_URL),
};
