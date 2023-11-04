/**
 * A route configuration object containing URL paths for the SvelteKit router.
 * URL paths are composed of current and parent key strings.
 * Routes contain nested configurations that contain the following:
 *
 * @param root {string} The canonical URL path for the route.
 * @param routes {object} [Additional nested route configurations.]
 */
/* eslint-disable max-lines-per-function, @typescript-eslint/explicit-function-return-type, no-shadow */
export default {
  root: "/",
  get routes() {
    return {
      tripManagement: {
        root: "/trip-management",
        get routes() {
          return {
            book: {
              root: `${this.root}/book`,
              get routes() {
                return {
                  select: { root: `${this.root}/select-offer` },
                  payment: { root: `${this.root}/payment` },
                  confirmation: { root: `${this.root}/confirmation` },
                } as const;
              },
            },
            orders: {
              root: `${this.root}/orders`,
              get routes() {
                return {
                  order: <TOrderId extends string>(id: TOrderId) =>
                    ({
                      root: `${this.root}/${id}`,
                      get routes() {
                        return {
                          tickets: { root: `${this.root}/tickets` },
                          details: { root: `${this.root}/details` },
                          booking: <TBookingId extends string>(id: TBookingId) =>
                            ({
                              root: `${this.root}/${id}`,
                              get routes() {
                                return { tickets: { root: `${this.root}/tickets` } } as const;
                              },
                            } as const),
                        } as const;
                      },
                    } as const),
                } as const;
              },
            },
          } as const;
        },
      },
      login: {
        root: "/login",
      },
      help: {
        root: "/help",
        get routes() {
          return {
            privacyPolicy: { root: `${this.root}/privacy-policy` },
            termsAndConditions: { root: `${this.root}/terms-and-conditions` },
            customerService: { root: `${this.root}/customer-service` },
            conditionsOfCarriage: { root: `${this.root}/conditions-of-carriage` },
          } as const;
        },
      },
      pay: {
        root: "/pay",
        get routes() {
          return {
            activity: {
              root: `${this.root}/activity`,
              get routes() {
                return {
                  conversions: {
                    root: `${this.root}/fx`,
                  } as const,
                } as const;
              },
            },
            accounts: {
              root: `${this.root}/accounts`,
              get routes() {
                return {
                  account: <TAccountId extends string>(id: TAccountId) =>
                    ({
                      root: `${this.root}/${id}`,
                    } as const),
                } as const;
              },
            },
            beneficiaries: {
              root: `${this.root}/beneficiaries`,
              get routes() {
                return {
                  beneficiary: <TBeneficiaryId extends string = "add">(
                    id: TBeneficiaryId = "add" as TBeneficiaryId,
                  ) => ({ root: `${this.root}/${id}` } as const),
                } as const;
              },
            },
            bills: {
              root: `${this.root}/bills`,
            },
          } as const;
        },
      },
      go: {
        root: "/go",
        get routes() {
          return {
            bookings: { root: `${this.root}/bookings` },
          } as const;
        },
      },
    } as const;
  },
} as const;
