import { env } from "$env/dynamic/private";
import junctionClientApi from "integration/junction-client-api/services";
import junctionMobileApi from "integration/junction-mobile-api/services";
import junctionPayApi from "integration/junction-pay/services";
import common from "integration/common/services";

const junctionPayCompanyService = new junctionPayApi.CompanyService(env.PAY_ADMIN_API_BASE_URL);

export default {
  junctionClientApi: {
    bookings: new junctionClientApi.BookingService(env.CLIENT_API_BASE_URL, env.CLIENT_API_KEY),
  },
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
    auth: new junctionPayApi.AuthenticationService(env.PAY_ADMIN_API_BASE_URL),
    accounts: new junctionPayApi.AccountService(env.PAY_ADMIN_API_BASE_URL),
    beneficiaries: new junctionPayApi.BeneficiaryService(env.PAY_ADMIN_API_BASE_URL),
    currencies: new junctionPayApi.CurrencyService(env.PAY_API_BASE_URL),
    conversions: new junctionPayApi.ConversionService(env.PAY_ADMIN_API_BASE_URL),
    companyService: junctionPayCompanyService,
    transactions: new junctionPayApi.TransactionService(
      env.PAY_ADMIN_API_BASE_URL,
      junctionPayCompanyService,
    ),
    balances: new junctionPayApi.BalanceService(env.PAY_ADMIN_API_BASE_URL),
  },
  common: {
    countries: new common.CountryService(),
  },
};
