type RouteConfig =
  | { root?: string; actions?: Record<string, string>; routes?: Record<string, RouteConfig> }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  | ((...args: any[]) => RouteConfig);

function getRouteConfig<TConfig extends RouteConfig>(config: TConfig): TConfig {
  return config;
}

/**
 * A route configuration object containing URL paths for the SvelteKit router.
 * URL paths are composed of current and parent key strings.
 * Routes contain nested configurations that contain the following:
 *
 * @param root {string} The canonical URL path for the route.
 * @param actions {object} [Key-value pairs of API actions and their URL paths.]
 * @param routes {object} [Additional nested route configurations.]
 */
export default getRouteConfig({
  root: "/",
  routes: {
    tripManagement: {
      root: "/trip-management",
      routes: {
        book: {
          root: "/trip-management/book",
          actions: {
            search: "/trip-management/book?/search",
            listPlaces: "/trip-management/book?/listPlaces",
          },
          routes: {
            select: {
              root: "/trip-management/book/select-offer",
              actions: {
                poll: "/trip-management/book/select-offer?/poll",
                select: "/trip-management/book/select-offer?/select",
              },
            },
            payment: {
              root: "/trip-management/book/payment",
              actions: {
                poll: "/trip-management/book/payment?/poll",
                createOrder: "/trip-management/book/payment?/createOrder",
                confirmPayment: "/trip-management/book/payment?/confirmPayment",
              },
            },
            confirmation: {
              root: "/trip-management/book/confirmation",
            },
          },
        },
        orders: {
          root: "/trip-management/orders",
          routes: {
            order<TId extends string>(
              id: TId,
            ): {
              root: `/trip-management/orders/${TId}`;
              routes: {
                details: {
                  root: `/trip-management/orders/${TId}/details`;
                };
                booking: <TBookingId extends string>(
                  bookingId: TBookingId,
                ) => {
                  root: `/trip-management/orders/${TId}/${TBookingId}`;
                };
              };
            } {
              const root = `/trip-management/orders/${id}` as const;

              return {
                root,
                routes: {
                  details: {
                    root: `${root}/details`,
                  },
                  booking<TBookingId extends string>(
                    bookingId: TBookingId,
                  ): {
                    root: `/trip-management/orders/${TId}/${TBookingId}`;
                  } {
                    return {
                      root: `${root}/${bookingId}`,
                    };
                  },
                },
              };
            },
          },
        },
      },
    },
    login: {
      root: "/login",
      actions: {
        login: "/login?/login",
        logout: "/login?/logout",
      },
    },
    help: {
      routes: {
        privacyPolicy: {
          root: "/help/privacy-policy",
        },
        termsAndConditions: {
          root: "/help/terms-and-conditions",
        },
        cookies: {
          root: "/help/cookies",
        },
        customerService: {
          root: "/help/customer-service",
        },
      },
    },
    settings: {
      root: "/settings",
    },
    pay: {
      root: "/pay",
      routes: {
        activity: {
          root: "/pay/activity",
          actions: {
            getBooking: "/pay/activity?/getBooking",
            listTransactions: "/pay/activity?/listTransactions",
          },
          routes: {
            conversions: {
              root: "/pay/activity/fx",
              actions: {
                listConversions: "/pay/activity/fx?/listConversions",
              },
            },
          },
        },
        accounts: {
          root: "/pay/accounts",
          actions: {
            listAccounts: "/pay/accounts?/listAccounts",
          },
          routes: {
            account<TId extends string>(
              id: TId,
            ): {
              root: `/pay/accounts/${TId}`;
              actions: {
                addBalances: `/pay/accounts/${TId}?/addBalances`;
              };
            } {
              const root = `/pay/accounts/${id}` as const;

              return {
                root,
                actions: {
                  addBalances: `${root}?/addBalances`,
                },
              };
            },
          },
        },
        beneficiaries: {
          root: "/pay/beneficiaries",
          actions: {
            listBeneficiaries: "/pay/beneficiaries?/listBeneficiaries",
          },
          routes: {
            beneficiary<
              TId extends string | undefined = undefined,
              TOut = `/pay/beneficiaries/${TId extends undefined ? "add" : TId}`,
            >(
              id?: TId,
            ): {
              root: TOut;
            } {
              return { root: `/pay/beneficiaries/${id ?? "add"}` as TOut };
            },
          },
        },
        bills: {
          root: "/pay/bills",
        },
      },
    },
    go: {
      root: "/go",
      routes: {
        bookings: {
          root: "/go/bookings",
        },
      },
    },
  },
} as const);
