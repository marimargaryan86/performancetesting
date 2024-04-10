export type Specification = {
  "/health": {
    get: {
      response: {
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { meta: { status: ("pass" | "fail" | "warn"); [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
    };
  };
  "/users": {
    get: {
      request?: {
        query?: {
          sort?: ("id" | "-id");
          "page[cursor]"?: string;
          "page[limit]"?: number;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "users"; attributes: { email: string; role: ("snowfall-admin" | "snowfall-user" | "reseller-admin" | "reseller-user"); [key: string]: unknown; }; relationships: { reseller: { data: { id: string; type: "resellers"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "users"; attributes: { email: string; role: ("snowfall-admin" | "snowfall-user" | "reseller-admin" | "reseller-user"); [key: string]: unknown; }; relationships: { reseller: { data: { id: string; type: "resellers"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "users"; attributes: { email: string; role: ("snowfall-admin" | "snowfall-user" | "reseller-admin" | "reseller-user"); [key: string]: unknown; }; relationships: { reseller: { data: { id: string; type: "resellers"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 409;
        body: {
          type: "application/vnd.api+json";
          data: { errors?: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 422;
        body: {
          type: "application/vnd.api+json";
          data: { errors?: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/users/{userId}": {
    get: {
      request: {
        path: {
          userId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "users"; attributes: { email: string; role: ("snowfall-admin" | "snowfall-user" | "reseller-admin" | "reseller-user"); [key: string]: unknown; }; relationships: { reseller: { data: { id: string; type: "resellers"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    delete: {
      request: {
        path: {
          userId: string;
        };
      };
      response: ({
        status: 204;
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    patch: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "users"; attributes: { email: string; role: ("snowfall-admin" | "snowfall-user" | "reseller-admin" | "reseller-user"); [key: string]: unknown; }; relationships: { reseller: { data: { id: string; type: "resellers"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          userId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "users"; attributes: { email: string; role: ("snowfall-admin" | "snowfall-user" | "reseller-admin" | "reseller-user"); [key: string]: unknown; }; relationships: { reseller: { data: { id: string; type: "resellers"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/users/me": {
    get: {
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "users-profiles"; attributes: { company: { name: string; address: { addressLines?: (string)[]; countryCode?: string; [key: string]: unknown; } & { postalCode: string; city: string; state: (string | null); [key: string]: unknown; }; [key: string]: unknown; }; contacts: ({ firstName: string; lastName: string; emailAddress: string; phoneNumber: string; [key: string]: unknown; })[]; permissions: { [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/activities": {
    get: {
      request?: {
        query?: {
          "page[cursor]"?: string;
          "page[limit]"?: number;
          "filter[orderIds][eq]"?: (string)[];
          "filter[departureDates][eq]"?: (string)[];
          "filter[transactionCreatedDates][eq]"?: (string)[];
          "filter[beneficiaryIds][eq]"?: (string)[];
          "filter[payerIds][eq]"?: (string)[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "activities"; attributes: { transactionCreatedAt: string; departureAt: string; baseConverted: { currency: string; amount: number; [key: string]: unknown; }; salesMargin: { currency: string; amount: number; [key: string]: unknown; }; quotation: { currency: string; amount: number; [key: string]: unknown; }; taxConverted: { currency: string; amount: number; [key: string]: unknown; }; totalAmount: { currency: string; amount: number; [key: string]: unknown; }; payerName: string; fxMargin: number; processingMargin: number; feeAmount: { currency: string; amount: number; [key: string]: unknown; }; totalMarkups: { currency: string; amount: number; [key: string]: unknown; }; beneficiaryAmount: { currency: string; amount: number; [key: string]: unknown; }; beneficiaryName: string; passengerName: string; paymentType: ("unspecified" | "card" | "bank-transfer"); paymentMethod: ("unspecified" | "transactional" | "invoice"); fxMarkup: number; salesMrkup?: number; processingMarkup: number; [key: string]: unknown; }; relationships?: { invoiceReference: { data: { id: string; type: "invoice-reference"; [key: string]: unknown; }; [key: string]: unknown; }; externalReference: { data: { id: string; type: "external-reference"; [key: string]: unknown; }; [key: string]: unknown; }; order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/activities/{transactionId}": {
    get: {
      request: {
        path: {
          transactionId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "activities"; attributes: { transactionCreatedAt: string; departureAt: string; baseConverted: { currency: string; amount: number; [key: string]: unknown; }; salesMargin: { currency: string; amount: number; [key: string]: unknown; }; quotation: { currency: string; amount: number; [key: string]: unknown; }; taxConverted: { currency: string; amount: number; [key: string]: unknown; }; totalAmount: { currency: string; amount: number; [key: string]: unknown; }; payerName: string; fxMargin: number; processingMargin: number; feeAmount: { currency: string; amount: number; [key: string]: unknown; }; totalMarkups: { currency: string; amount: number; [key: string]: unknown; }; beneficiaryAmount: { currency: string; amount: number; [key: string]: unknown; }; beneficiaryName: string; passengerName: string; paymentType: ("unspecified" | "card" | "bank-transfer"); paymentMethod: ("unspecified" | "transactional" | "invoice"); fxMarkup: number; salesMrkup?: number; processingMarkup: number; [key: string]: unknown; }; relationships?: { invoiceReference: { data: { id: string; type: "invoice-reference"; [key: string]: unknown; }; [key: string]: unknown; }; externalReference: { data: { id: string; type: "external-reference"; [key: string]: unknown; }; [key: string]: unknown; }; order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/bookings/{bookingId}": {
    get: {
      request: {
        path: {
          bookingId: string;
        };
        query?: {
          include?: (("order" | "order.journey" | "details" | "bookingCancellation" | "transaction" | "refund"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; operatorBookingReferences: (string)[]; externalReference: string; rules?: ({ title: string; body: string; [key: string]: unknown; })[]; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; bookingCancellation: { data: { id: string; type: "booking-cancellation"; [key: string]: unknown; }; [key: string]: unknown; } | null; transaction: { data: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; } | null; refund: { data: { id: string; type: "refunds"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; included?: ({ id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "booking-cancellation"; attributes: { status: ("unspecified" | "pending" | "completed" | "rejected" | "no-refund" | "refund-due" | "refund-issued" | "refund-failed"); [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "transactions"; attributes: { externalReference: string; invoiceReference?: string; createdAt: string; amounts: { beneficiary: { currency: string; amount: number; [key: string]: unknown; }; quotation: { currency: string; amount: number; [key: string]: unknown; }; baseConverted: { currency: string; amount: number; [key: string]: unknown; }; salesMargin: { currency: string; amount: number; [key: string]: unknown; }; fxMargin: { currency: string; amount: number; [key: string]: unknown; }; processingMargin: { currency: string; amount: number; [key: string]: unknown; }; totalAmount: { currency: string; amount: number; [key: string]: unknown; }; [key: string]: unknown; }; rates: { fxQuote: number; fxBuffer: number; salesMarkup: number; fxMarkup: number; processingMarkup: number; [key: string]: unknown; }; paymentType: ("unspecified" | "card" | "bank-transfer"); paymentMethod: ("unspecified" | "transactional" | "invoice"); [key: string]: unknown; }; relationships?: { bill?: { data: ({ id: string; type: "bills"; [key: string]: unknown; } | null | null); [key: string]: unknown; }; payer?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; beneficiary?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "refunds"; attributes: { status: ("pending" | "succeeded" | "failed" | "submitted"); refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedUsInPayerCurrency?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundPosition?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/journeys": {
    get: {
      request?: {
        query?: {
          sort?: ("id" | "-id" | "reference" | "-reference" | "createdAt" | "-createdAt" | "passengerLastName" | "-passengerLastName");
          include?: (("orders" | "orders.bookings" | "orders.bookings.details" | "orders.bookings.bookingCancellation" | "orders.bookings.transaction" | "orders.bookings.refund"))[];
          "filter[createdAt][le]"?: string;
          "filter[createdAt][ge]"?: string;
          "filter[departureDate][ge]"?: string;
          "filter[departureDate][le]"?: string;
          "filter[status][eq]"?: (("unspecified" | "pending" | "confirmed" | "rejected" | "not-ticketed" | "error" | "cancelled"))[];
          "filter[passengerLastName][like]"?: string;
          "filter[passengerLastName][eq]"?: undefined;
          "filter[pnr][eq]"?: undefined;
          "page[cursor]"?: string;
          "page[limit]"?: number;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; included?: ({ id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; operatorBookingReferences: (string)[]; externalReference: string; rules?: ({ title: string; body: string; [key: string]: unknown; })[]; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; bookingCancellation: { data: { id: string; type: "booking-cancellation"; [key: string]: unknown; }; [key: string]: unknown; } | null; transaction: { data: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; } | null; refund: { data: { id: string; type: "refunds"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "booking-cancellation"; attributes: { status: ("unspecified" | "pending" | "completed" | "rejected" | "no-refund" | "refund-due" | "refund-issued" | "refund-failed"); [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "transactions"; attributes: { externalReference: string; invoiceReference?: string; createdAt: string; amounts: { beneficiary: { currency: string; amount: number; [key: string]: unknown; }; quotation: { currency: string; amount: number; [key: string]: unknown; }; baseConverted: { currency: string; amount: number; [key: string]: unknown; }; salesMargin: { currency: string; amount: number; [key: string]: unknown; }; fxMargin: { currency: string; amount: number; [key: string]: unknown; }; processingMargin: { currency: string; amount: number; [key: string]: unknown; }; totalAmount: { currency: string; amount: number; [key: string]: unknown; }; [key: string]: unknown; }; rates: { fxQuote: number; fxBuffer: number; salesMarkup: number; fxMarkup: number; processingMarkup: number; [key: string]: unknown; }; paymentType: ("unspecified" | "card" | "bank-transfer"); paymentMethod: ("unspecified" | "transactional" | "invoice"); [key: string]: unknown; }; relationships?: { bill?: { data: ({ id: string; type: "bills"; [key: string]: unknown; } | null | null); [key: string]: unknown; }; payer?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; beneficiary?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "refunds"; attributes: { status: ("pending" | "succeeded" | "failed" | "submitted"); refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedUsInPayerCurrency?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundPosition?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/journeys/{journeyId}": {
    get: {
      request: {
        path: {
          journeyId: string;
        };
        query?: {
          include?: (("orders" | "orders.bookings" | "orders.bookings.details" | "orders.bookings.bookingCancellation" | "orders.bookings.transaction" | "orders.bookings.refund"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; included?: ({ id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; operatorBookingReferences: (string)[]; externalReference: string; rules?: ({ title: string; body: string; [key: string]: unknown; })[]; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; bookingCancellation: { data: { id: string; type: "booking-cancellation"; [key: string]: unknown; }; [key: string]: unknown; } | null; transaction: { data: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; } | null; refund: { data: { id: string; type: "refunds"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "booking-cancellation"; attributes: { status: ("unspecified" | "pending" | "completed" | "rejected" | "no-refund" | "refund-due" | "refund-issued" | "refund-failed"); [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "transactions"; attributes: { externalReference: string; invoiceReference?: string; createdAt: string; amounts: { beneficiary: { currency: string; amount: number; [key: string]: unknown; }; quotation: { currency: string; amount: number; [key: string]: unknown; }; baseConverted: { currency: string; amount: number; [key: string]: unknown; }; salesMargin: { currency: string; amount: number; [key: string]: unknown; }; fxMargin: { currency: string; amount: number; [key: string]: unknown; }; processingMargin: { currency: string; amount: number; [key: string]: unknown; }; totalAmount: { currency: string; amount: number; [key: string]: unknown; }; [key: string]: unknown; }; rates: { fxQuote: number; fxBuffer: number; salesMarkup: number; fxMarkup: number; processingMarkup: number; [key: string]: unknown; }; paymentType: ("unspecified" | "card" | "bank-transfer"); paymentMethod: ("unspecified" | "transactional" | "invoice"); [key: string]: unknown; }; relationships?: { bill?: { data: ({ id: string; type: "bills"; [key: string]: unknown; } | null | null); [key: string]: unknown; }; payer?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; beneficiary?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "refunds"; attributes: { status: ("pending" | "succeeded" | "failed" | "submitted"); refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedUsInPayerCurrency?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundPosition?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/journeys/{journeyId}/orders": {
    get: {
      request: {
        path: {
          journeyId: string;
        };
        query?: {
          sort?: "id";
          "page[cursor]"?: string;
          "page[limit]"?: number;
          include?: (("journey" | "bookings" | "bookings.details" | "bookings.bookingCancellation" | "bookings.transaction" | "bookings.refund"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; included?: ({ id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; operatorBookingReferences: (string)[]; externalReference: string; rules?: ({ title: string; body: string; [key: string]: unknown; })[]; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; bookingCancellation: { data: { id: string; type: "booking-cancellation"; [key: string]: unknown; }; [key: string]: unknown; } | null; transaction: { data: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; } | null; refund: { data: { id: string; type: "refunds"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/orders/{orderId}": {
    get: {
      request: {
        path: {
          orderId: string;
        };
        query?: {
          include?: (("journey" | "bookings" | "bookings.details" | "bookings.bookingCancellation" | "bookings.transaction" | "bookings.refund"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; included?: ({ id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; operatorBookingReferences: (string)[]; externalReference: string; rules?: ({ title: string; body: string; [key: string]: unknown; })[]; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; bookingCancellation: { data: { id: string; type: "booking-cancellation"; [key: string]: unknown; }; [key: string]: unknown; } | null; transaction: { data: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; } | null; refund: { data: { id: string; type: "refunds"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "booking-cancellation"; attributes: { status: ("unspecified" | "pending" | "completed" | "rejected" | "no-refund" | "refund-due" | "refund-issued" | "refund-failed"); [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "transactions"; attributes: { externalReference: string; invoiceReference?: string; createdAt: string; amounts: { beneficiary: { currency: string; amount: number; [key: string]: unknown; }; quotation: { currency: string; amount: number; [key: string]: unknown; }; baseConverted: { currency: string; amount: number; [key: string]: unknown; }; salesMargin: { currency: string; amount: number; [key: string]: unknown; }; fxMargin: { currency: string; amount: number; [key: string]: unknown; }; processingMargin: { currency: string; amount: number; [key: string]: unknown; }; totalAmount: { currency: string; amount: number; [key: string]: unknown; }; [key: string]: unknown; }; rates: { fxQuote: number; fxBuffer: number; salesMarkup: number; fxMarkup: number; processingMarkup: number; [key: string]: unknown; }; paymentType: ("unspecified" | "card" | "bank-transfer"); paymentMethod: ("unspecified" | "transactional" | "invoice"); [key: string]: unknown; }; relationships?: { bill?: { data: ({ id: string; type: "bills"; [key: string]: unknown; } | null | null); [key: string]: unknown; }; payer?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; beneficiary?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "refunds"; attributes: { status: ("pending" | "succeeded" | "failed" | "submitted"); refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedUsInPayerCurrency?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundPosition?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/orders/{orderId}/bookings": {
    get: {
      request: {
        path: {
          orderId: string;
        };
        query?: {
          sort?: "id";
          "page[cursor]"?: string;
          "page[limit]"?: number;
          include?: (("order" | "order.journey" | "details" | "bookingCancellation" | "transaction" | "refund"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; operatorBookingReferences: (string)[]; externalReference: string; rules?: ({ title: string; body: string; [key: string]: unknown; })[]; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; bookingCancellation: { data: { id: string; type: "booking-cancellation"; [key: string]: unknown; }; [key: string]: unknown; } | null; transaction: { data: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; } | null; refund: { data: { id: string; type: "refunds"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; included?: ({ id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "booking-cancellation"; attributes: { status: ("unspecified" | "pending" | "completed" | "rejected" | "no-refund" | "refund-due" | "refund-issued" | "refund-failed"); [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "transactions"; attributes: { externalReference: string; invoiceReference?: string; createdAt: string; amounts: { beneficiary: { currency: string; amount: number; [key: string]: unknown; }; quotation: { currency: string; amount: number; [key: string]: unknown; }; baseConverted: { currency: string; amount: number; [key: string]: unknown; }; salesMargin: { currency: string; amount: number; [key: string]: unknown; }; fxMargin: { currency: string; amount: number; [key: string]: unknown; }; processingMargin: { currency: string; amount: number; [key: string]: unknown; }; totalAmount: { currency: string; amount: number; [key: string]: unknown; }; [key: string]: unknown; }; rates: { fxQuote: number; fxBuffer: number; salesMarkup: number; fxMarkup: number; processingMarkup: number; [key: string]: unknown; }; paymentType: ("unspecified" | "card" | "bank-transfer"); paymentMethod: ("unspecified" | "transactional" | "invoice"); [key: string]: unknown; }; relationships?: { bill?: { data: ({ id: string; type: "bills"; [key: string]: unknown; } | null | null); [key: string]: unknown; }; payer?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; beneficiary?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "refunds"; attributes: { status: ("pending" | "succeeded" | "failed" | "submitted"); refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedUsInPayerCurrency?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundPosition?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/bookings/{bookingId}/cancellation": {
    get: {
      request: {
        path: {
          bookingId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "booking-cancellation"; attributes: { status: ("unspecified" | "pending" | "completed" | "rejected" | "no-refund" | "refund-due" | "refund-issued" | "refund-failed"); [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/bookings/{bookingId}/details": {
    get: {
      request: {
        path: {
          bookingId: string;
        };
        query?: {
          sort?: "id";
          "page[cursor]"?: string;
          "page[limit]"?: number;
          include?: (("booking" | "booking.order" | "booking.order.journey"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; included?: ({ id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; operatorBookingReferences: (string)[]; externalReference: string; rules?: ({ title: string; body: string; [key: string]: unknown; })[]; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; bookingCancellation: { data: { id: string; type: "booking-cancellation"; [key: string]: unknown; }; [key: string]: unknown; } | null; transaction: { data: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; } | null; refund: { data: { id: string; type: "refunds"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/bookings/details/{bookingDetailsId}": {
    get: {
      request: {
        path: {
          bookingDetailsId: string;
        };
        query?: {
          include?: (("booking" | "booking.order" | "booking.order.journey"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; included?: ({ id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; operatorBookingReferences: (string)[]; externalReference: string; rules?: ({ title: string; body: string; [key: string]: unknown; })[]; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; bookingCancellation: { data: { id: string; type: "booking-cancellation"; [key: string]: unknown; }; [key: string]: unknown; } | null; transaction: { data: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; } | null; refund: { data: { id: string; type: "refunds"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/cancellations/requests": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "cancellation-request"; relationships: { bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "cancellation-request"; attributes: { status: ("unspecified" | "pending" | "completed"); [key: string]: unknown; }; relationships: { bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 422;
        body: {
          type: "application/vnd.api+json";
          data: { errors?: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/cancellations/requests/{cancellationRequestId}": {
    get: {
      request: {
        path: {
          cancellationRequestId: string;
        };
        query?: {
          include?: (("bookings" | "bookings.order" | "bookings.order.journey" | "bookings.details"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "cancellation-request"; attributes: { status: ("unspecified" | "pending" | "completed"); [key: string]: unknown; }; relationships: { bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; included?: ({ id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; operatorBookingReferences: (string)[]; externalReference: string; rules?: ({ title: string; body: string; [key: string]: unknown; })[]; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; bookingCancellation: { data: { id: string; type: "booking-cancellation"; [key: string]: unknown; }; [key: string]: unknown; } | null; transaction: { data: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; } | null; refund: { data: { id: string; type: "refunds"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/companies": {
    get: {
      request?: {
        query?: {
          "page[cursor]"?: string;
          "page[limit]"?: number;
          "filter[type][eq]"?: (("reseller" | "provider"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "companies"; attributes: { name?: string; address?: { addressLines?: (string)[]; countryCode?: string; [key: string]: unknown; } & { postalCode: string; city: string; state: (string | null); [key: string]: unknown; }; fxMarkup?: number; processingMarkup?: number; salesMarkup?: number; feeAmounts?: ({ currency: string; amount: number; [key: string]: unknown; })[]; paymentType?: ("unspecified" | "card" | "bank-transfer"); billingType?: ("unspecified" | "percentage" | "fixed"); paymentMethod?: ("unspecified" | "transactional" | "invoice"); applyMarkups?: boolean; invoiceGenerationFrequency?: number; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "companies"; attributes: { name?: string; address?: { addressLines?: (string)[]; countryCode?: string; [key: string]: unknown; } & { postalCode: string; city: string; state: (string | null); [key: string]: unknown; }; fxMarkup?: number; processingMarkup?: number; salesMarkup?: number; feeAmounts?: ({ currency: string; amount: number; [key: string]: unknown; })[]; paymentType?: ("unspecified" | "card" | "bank-transfer"); billingType?: ("unspecified" | "percentage" | "fixed"); paymentMethod?: ("unspecified" | "transactional" | "invoice"); applyMarkups?: boolean; invoiceGenerationFrequency?: number; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "companies"; attributes: { name?: string; address?: { addressLines?: (string)[]; countryCode?: string; [key: string]: unknown; } & { postalCode: string; city: string; state: (string | null); [key: string]: unknown; }; fxMarkup?: number; processingMarkup?: number; salesMarkup?: number; feeAmounts?: ({ currency: string; amount: number; [key: string]: unknown; })[]; paymentType?: ("unspecified" | "card" | "bank-transfer"); billingType?: ("unspecified" | "percentage" | "fixed"); paymentMethod?: ("unspecified" | "transactional" | "invoice"); applyMarkups?: boolean; invoiceGenerationFrequency?: number; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/companies/{companyId}": {
    get: {
      request: {
        path: {
          companyId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data?: { id: string; type: "companies"; attributes: { name?: string; address?: { addressLines?: (string)[]; countryCode?: string; [key: string]: unknown; } & { postalCode: string; city: string; state: (string | null); [key: string]: unknown; }; fxMarkup?: number; processingMarkup?: number; salesMarkup?: number; feeAmounts?: ({ currency: string; amount: number; [key: string]: unknown; })[]; paymentType?: ("unspecified" | "card" | "bank-transfer"); billingType?: ("unspecified" | "percentage" | "fixed"); paymentMethod?: ("unspecified" | "transactional" | "invoice"); applyMarkups?: boolean; invoiceGenerationFrequency?: number; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    patch: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "companies"; attributes: { name?: string; address?: { addressLines?: (string)[]; countryCode?: string; [key: string]: unknown; } & { postalCode: string; city: string; state: (string | null); [key: string]: unknown; }; fxMarkup?: number; processingMarkup?: number; salesMarkup?: number; feeAmounts?: ({ currency: string; amount: number; [key: string]: unknown; })[]; paymentType?: ("unspecified" | "card" | "bank-transfer"); billingType?: ("unspecified" | "percentage" | "fixed"); paymentMethod?: ("unspecified" | "transactional" | "invoice"); applyMarkups?: boolean; invoiceGenerationFrequency?: number; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          companyId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "companies"; attributes: { name?: string; address?: { addressLines?: (string)[]; countryCode?: string; [key: string]: unknown; } & { postalCode: string; city: string; state: (string | null); [key: string]: unknown; }; fxMarkup?: number; processingMarkup?: number; salesMarkup?: number; feeAmounts?: ({ currency: string; amount: number; [key: string]: unknown; })[]; paymentType?: ("unspecified" | "card" | "bank-transfer"); billingType?: ("unspecified" | "percentage" | "fixed"); paymentMethod?: ("unspecified" | "transactional" | "invoice"); applyMarkups?: boolean; invoiceGenerationFrequency?: number; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/companies/{companyId}/contacts": {
    get: {
      request: {
        path: {
          companyId: string;
        };
        query?: {
          "page[cursor]"?: string;
          "page[limit]"?: number;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "contacts"; attributes: { firstName: string; lastName: string; emailAddress: string; phoneNumber: string; [key: string]: unknown; }; relationships: { company: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "contacts"; attributes: { firstName: string; lastName: string; emailAddress: string; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          companyId: string;
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "contacts"; attributes: { firstName: string; lastName: string; emailAddress: string; phoneNumber: string; [key: string]: unknown; }; relationships: { company: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/transactions/{transactionId}": {
    get: {
      request: {
        path: {
          transactionId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "transactions"; attributes: { externalReference: string; invoiceReference?: string; createdAt: string; amounts: { beneficiary: { currency: string; amount: number; [key: string]: unknown; }; quotation: { currency: string; amount: number; [key: string]: unknown; }; baseConverted: { currency: string; amount: number; [key: string]: unknown; }; salesMargin: { currency: string; amount: number; [key: string]: unknown; }; fxMargin: { currency: string; amount: number; [key: string]: unknown; }; processingMargin: { currency: string; amount: number; [key: string]: unknown; }; totalAmount: { currency: string; amount: number; [key: string]: unknown; }; [key: string]: unknown; }; rates: { fxQuote: number; fxBuffer: number; salesMarkup: number; fxMarkup: number; processingMarkup: number; [key: string]: unknown; }; paymentType: ("unspecified" | "card" | "bank-transfer"); paymentMethod: ("unspecified" | "transactional" | "invoice"); [key: string]: unknown; }; relationships?: { bill?: { data: ({ id: string; type: "bills"; [key: string]: unknown; } | null | null); [key: string]: unknown; }; payer?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; beneficiary?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/transactions": {
    get: {
      request?: {
        query?: {
          "page[cursor]"?: string;
          "page[limit]"?: number;
          sort?: ("createdAt" | "-createdAt");
          "filter[ids][eq]"?: (string)[];
          "filter[bill.id][eq]"?: (string)[];
          "filter[externalReference][eq]"?: (string)[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "transactions"; attributes: { externalReference: string; invoiceReference?: string; createdAt: string; amounts: { beneficiary: { currency: string; amount: number; [key: string]: unknown; }; quotation: { currency: string; amount: number; [key: string]: unknown; }; baseConverted: { currency: string; amount: number; [key: string]: unknown; }; salesMargin: { currency: string; amount: number; [key: string]: unknown; }; fxMargin: { currency: string; amount: number; [key: string]: unknown; }; processingMargin: { currency: string; amount: number; [key: string]: unknown; }; totalAmount: { currency: string; amount: number; [key: string]: unknown; }; [key: string]: unknown; }; rates: { fxQuote: number; fxBuffer: number; salesMarkup: number; fxMarkup: number; processingMarkup: number; [key: string]: unknown; }; paymentType: ("unspecified" | "card" | "bank-transfer"); paymentMethod: ("unspecified" | "transactional" | "invoice"); [key: string]: unknown; }; relationships?: { bill?: { data: ({ id: string; type: "bills"; [key: string]: unknown; } | null | null); [key: string]: unknown; }; payer?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; beneficiary?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/bills": {
    get: {
      request?: {
        query?: {
          "page[cursor]"?: string;
          "page[limit]"?: number;
          sort?: ("updatedAt" | "-updatedAt");
          "filter[order.id][eq]"?: (string)[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "bills"; attributes?: { createdAt?: string; updatedAt?: string; isReconciled?: boolean; totalAmount?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); reconciledAmount?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); [key: string]: unknown; }; relationships?: { order?: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/bills/{billId}": {
    get: {
      request: {
        path: {
          billId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data?: { id: string; type: "bills"; attributes?: { createdAt?: string; updatedAt?: string; isReconciled?: boolean; totalAmount?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); reconciledAmount?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); [key: string]: unknown; }; relationships?: { order?: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    patch: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "bills"; attributes?: { createdAt?: string; updatedAt?: string; isReconciled?: boolean; [key: string]: unknown; }; relationships?: { [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          billId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "bills"; attributes?: { createdAt?: string; updatedAt?: string; isReconciled?: boolean; totalAmount?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); reconciledAmount?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); [key: string]: unknown; }; relationships?: { order?: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/refunds": {
    get: {
      request?: {
        query?: {
          "page[cursor]"?: string;
          "page[limit]"?: number;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "refunds"; attributes: { status: ("pending" | "succeeded" | "failed" | "submitted"); refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedUsInPayerCurrency?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundPosition?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "refunds"; attributes: { refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "refunds"; attributes: { status: ("pending" | "succeeded" | "failed" | "submitted"); refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedUsInPayerCurrency?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundPosition?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/refunds/{refundId}": {
    get: {
      request: {
        path: {
          refundId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "refunds"; attributes: { status: ("pending" | "succeeded" | "failed" | "submitted"); refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedUsInPayerCurrency?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundPosition?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    patch: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "refunds"; attributes: { refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; } | { type: "refunds"; attributes: { externalReference: string; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          refundId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "refunds"; attributes: { status: ("pending" | "succeeded" | "failed" | "submitted"); refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedUsInPayerCurrency?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundPosition?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/refunds/bookings/{bookingId}": {
    get: {
      request: {
        path: {
          bookingId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "refunds"; attributes: { status: ("pending" | "succeeded" | "failed" | "submitted"); refundReceived: boolean; note: string; refundedUs: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedUsInPayerCurrency?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundedReseller: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); refundPosition?: ({ currency: string; amount: number; [key: string]: unknown; } | null | null); invoiceReference: string; externalReference?: string; [key: string]: unknown; }; relationships: { transaction: { data?: { id: string; type: "transactions"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/refunds/{refundId}/refund-position": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "refund-position"; attributes: { refundedUs: { currency: string; amount: number; [key: string]: unknown; }; refundedReseller: { currency: string; amount: number; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          refundId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "refund-position"; attributes: { refundPosition?: ({ [key: string]: unknown; } & { currency: string; amount: number; [key: string]: unknown; }); [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/currencies": {
    get: {
      request?: {
        query?: {
          "page[cursor]"?: string;
          "page[limit]"?: number;
          sort?: "id";
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "currencies"; attributes: { name: string; minorUnits: number; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/currencies/{currencyName}": {
    get: {
      request: {
        path: {
          currencyName: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "currencies"; attributes: { name: string; minorUnits: number; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/payments": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "payments"; attributes: { amount: string; currency: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data?: { id: string; type: "payments"; attributes: { clientSecret: string; ephemeralKey: string; [key: string]: unknown; }; relationships?: { stripeCustomer?: { data: { id: string; type: "stripe-customer"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/resellers": {
    get: {
      request?: {
        query?: {
          "page[cursor]"?: string;
          "page[limit]"?: number;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "resellers"; attributes: { name?: string; providers?: (string)[]; [key: string]: unknown; }; relationships?: { company?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; currency?: { data: { id: string; type: "currencies"; [key: string]: unknown; }; [key: string]: unknown; }; parentResellers?: { data: ({ id: string; type: "resellers"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "resellers"; attributes: { name?: string; providers?: (string)[]; [key: string]: unknown; }; relationships?: { company?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; currency?: { data: { id: string; type: "currencies"; [key: string]: unknown; }; [key: string]: unknown; }; parentResellers?: { data: ({ id: string; type: "resellers"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "resellers"; attributes: { name?: string; providers?: (string)[]; [key: string]: unknown; }; relationships?: { company?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; currency?: { data: { id: string; type: "currencies"; [key: string]: unknown; }; [key: string]: unknown; }; parentResellers?: { data: ({ id: string; type: "resellers"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/resellers/{resellerId}": {
    get: {
      request: {
        path: {
          resellerId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data?: { id: string; type: "resellers"; attributes: { name?: string; providers?: (string)[]; [key: string]: unknown; }; relationships?: { company?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; currency?: { data: { id: string; type: "currencies"; [key: string]: unknown; }; [key: string]: unknown; }; parentResellers?: { data: ({ id: string; type: "resellers"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    delete: {
      request: {
        path: {
          resellerId: string;
        };
      };
      response: ({
        status: 204;
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    patch: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "resellers"; attributes: { name?: string; providers?: (string)[]; [key: string]: unknown; }; relationships?: { company?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; currency?: { data: { id: string; type: "currencies"; [key: string]: unknown; }; [key: string]: unknown; }; parentResellers?: { data: ({ id: string; type: "resellers"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          resellerId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "resellers"; attributes: { name?: string; providers?: (string)[]; [key: string]: unknown; }; relationships?: { company?: { data: { id: string; type: "companies"; [key: string]: unknown; }; [key: string]: unknown; }; currency?: { data: { id: string; type: "currencies"; [key: string]: unknown; }; [key: string]: unknown; }; parentResellers?: { data: ({ id: string; type: "resellers"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/resellers/plus-services-access/{resellerId}": {
    get: {
      request: {
        path: {
          resellerId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "plus-services-access"; attributes: { ref: string; displayName: string; enabled: boolean; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
    patch: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ type: "plus-services-access"; attributes: { ref: string; enabled: boolean; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
        path: {
          resellerId: string;
        };
      };
      response: ({
        status: 204;
      } | {
        status: 400;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      } | {
        status: 401;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
};
