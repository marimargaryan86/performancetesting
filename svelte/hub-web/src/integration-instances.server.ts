import { env } from "$env/dynamic/private";
import junctionMobileApi from "integration/junction-mobile-api/services";
import junctionPayApi from "integration/junction-hub-api/services";
import common from "integration/common/services";
import ory from "integration/ory/services";

const junctionPayCompanyService = new junctionPayApi.CompanyService(env.HUB_API_BASE_URL);

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
  junctionPayApi: {
    accounts: new junctionPayApi.AccountService(env.HUB_API_BASE_URL),
    beneficiaries: new junctionPayApi.BeneficiaryService(env.HUB_API_BASE_URL),
    currencies: new junctionPayApi.CurrencyService(env.HUB_API_BASE_URL),
    conversions: new junctionPayApi.ConversionService(env.HUB_API_BASE_URL),
    companyService: junctionPayCompanyService,
    transactions: new junctionPayApi.TransactionService(
      env.HUB_API_BASE_URL,
      junctionPayCompanyService,
    ),
    bookings: new junctionPayApi.BookingService(env.HUB_API_BASE_URL),
    balances: new junctionPayApi.BalanceService(env.HUB_API_BASE_URL),
    bills: new junctionPayApi.BillService(env.HUB_API_BASE_URL),
  },
  common: {
    countries: new common.CountryService(),
  },
  ory: new ory.OryService(env.ORY_BASE_URL),
};
