/**
 * A route configuration object containing URL paths for the SvelteKit router.
 * URL paths are composed of current and parent key strings.
 * Routes contain nested configurations that contain the following:
 *
 * @param root {string} The canonical URL path for the route.
 * @param actions {object} [Key-value pairs of API actions and their URL paths.]
 * @param routes {object} [Additional nested route configurations.]
 */
export default {
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
            order: <TOrderId extends string>(orderId: TOrderId) =>
              ({
                root: `/trip-management/orders/${orderId}`,
                actions: {
                  cancelBookings: `/trip-management/orders/${orderId}?/cancelBookings`,
                },
                routes: {
                  tickets: {
                    root: `/trip-management/orders/${orderId}/tickets`,
                  },
                  details: {
                    root: `/trip-management/orders/${orderId}/details`,
                  },
                  booking: <TBookingId extends string>(bookingId: TBookingId) =>
                    ({
                      root: `/trip-management/orders/${orderId}/${bookingId}`,
                      routes: {
                        tickets: {
                          root: `/trip-management/orders/${orderId}/${bookingId}/tickets`,
                        },
                      },
                    } as const),
                },
              } as const),
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
        customerService: {
          root: "/help/customer-service",
        },
        conditionsOfCarriage: {
          root: "/help/conditions-of-carriage",
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
            account: <TAccountId extends string>(accountId: TAccountId) =>
              ({
                root: `/pay/accounts/${accountId}`,
                actions: {
                  addBalances: `/pay/accounts/${accountId}?/addBalances`,
                },
              } as const),
          },
        },
        beneficiaries: {
          root: "/pay/beneficiaries",
          actions: {
            listBeneficiaries: "/pay/beneficiaries?/listBeneficiaries",
          },
          routes: {
            beneficiary: <TBeneficiaryId extends string = "add">(
              beneficiaryId: TBeneficiaryId = "add" as TBeneficiaryId,
            ) =>
              ({
                root: `/pay/beneficiaries/${beneficiaryId}`,
              } as const),
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
} as const;
