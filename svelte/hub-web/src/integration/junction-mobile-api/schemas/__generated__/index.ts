export type Specification = {
  "/guests": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "guests"; attributes?: { [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "guests"; attributes?: { createdAt: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
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
  "/guests/sessions": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data?: { type: "guest-sessions"; relationships: { guest: { data: { id: string; type: "guests"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data?: { id: string; type: "guest-sessions"; relationships: { guest: { data: { id: string; type: "guests"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/cabin-classes": {
    get: {
      request?: {
        query?: {
          sort?: "id";
          "page[cursor]"?: string;
          "page[limit]"?: number;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "cabin-classes"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/passengers/genders": {
    get: {
      request?: {
        query?: {
          sort?: "id";
          "page[cursor]"?: string;
          "page[limit]"?: number;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "passenger-genders"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/passengers/titles": {
    get: {
      request?: {
        query?: {
          sort?: "id";
          "page[cursor]"?: string;
          "page[limit]"?: number;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "passenger-titles"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/users/groups": {
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
          data: { data: ({ id: string; type: "user-groups"; attributes: { name: string; createdAt?: string; updatedAt?: string; [key: string]: unknown; }; relationships: { members: { data: ({ id: string; type: "user-group-members"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
          data: { data: { type: "user-groups"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "user-groups"; attributes: { name: string; createdAt?: string; updatedAt?: string; [key: string]: unknown; }; relationships: { members: { data: ({ id: string; type: "user-group-members"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/users/groups/{groupId}": {
    get: {
      request: {
        path: {
          groupId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "user-groups"; attributes: { name: string; createdAt?: string; updatedAt?: string; [key: string]: unknown; }; relationships: { members: { data: ({ id: string; type: "user-group-members"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
          groupId: string;
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
          data: { data: { type: "user-groups"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          groupId: string;
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
  "/users/groups/{groupId}/members": {
    get: {
      request: {
        path: {
          groupId: string;
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
          data: { data: ({ id: string; type: "user-group-members"; [key: string]: unknown; } & { attributes: { firstName?: string; lastName?: string; email?: string; phone?: string; gender?: ("female" | "male" | "unspecified"); title?: ("mr" | "mrs" | "miss" | "ms"); countryCode?: string; dateOfBirth?: string; loyaltyPrograms?: ({ program: string; number: string; [key: string]: unknown; })[]; createdAt?: string; updatedAt?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "user-group-members"; [key: string]: unknown; } & { attributes: { firstName?: string; lastName?: string; email?: string; phone?: string; gender?: ("female" | "male" | "unspecified"); title?: ("mr" | "mrs" | "miss" | "ms"); countryCode?: string; dateOfBirth?: string; loyaltyPrograms?: ({ program: string; number: string; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          groupId: string;
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "user-group-members"; [key: string]: unknown; } & { attributes: { firstName?: string; lastName?: string; email?: string; phone?: string; gender?: ("female" | "male" | "unspecified"); title?: ("mr" | "mrs" | "miss" | "ms"); countryCode?: string; dateOfBirth?: string; loyaltyPrograms?: ({ program: string; number: string; [key: string]: unknown; })[]; createdAt?: string; updatedAt?: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/users/groups/members/{memberId}": {
    delete: {
      request: {
        path: {
          memberId: string;
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
          data: { data: { type: "user-group-members"; [key: string]: unknown; } & { attributes: { firstName?: string; lastName?: string; email?: string; phone?: string; gender?: ("female" | "male" | "unspecified"); title?: ("mr" | "mrs" | "miss" | "ms"); countryCode?: string; dateOfBirth?: string; loyaltyPrograms?: ({ program: string; number: string; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          memberId: string;
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
  "/vouchers/{voucherCode}": {
    get: {
      request: {
        path: {
          voucherCode: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "vouchers"; attributes: { code: string; expiresAt: string; price: { currency: string; amount: string; [key: string]: unknown; }; status: ("used" | "valid" | "expired"); [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/push-notifications/tokens": {
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
          data: { data?: ({ id: string; type: "push-notification-tokens"; attributes: { deviceToken: string; createdAt: string; updatedAt?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "push-notification-tokens"; attributes: { notificationToken: string; deviceToken: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "push-notification-tokens"; attributes: { deviceToken: string; createdAt: string; updatedAt?: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
    patch: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "push-notification-tokens"; attributes: { notificationToken: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/push-notifications/tokens/{deviceToken}": {
    get: {
      request: {
        path: {
          deviceToken: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "push-notification-tokens"; attributes: { deviceToken: string; createdAt: string; updatedAt?: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
          deviceToken: string;
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
          data: { data: { type: "push-notification-tokens"; attributes: { notificationToken: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          deviceToken: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "push-notification-tokens"; attributes: { deviceToken: string; createdAt: string; updatedAt?: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/trips/searches": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "trip-searches"; attributes: { departureAfter?: string; departureBefore?: (string | null); arrivalBefore?: string; maximumConnections?: number; [key: string]: unknown; }; relationships: { origin: { data: { id: string; type: "places"; [key: string]: unknown; }; [key: string]: unknown; }; destination: { data: { id: string; type: "places"; [key: string]: unknown; }; [key: string]: unknown; }; allowedSegmentTypes?: { data: ({ id: string; type: "leg-types"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "trip-searches"; attributes: { expiresAt: string; departureAfter?: string; departureBefore?: (string | null); arrivalBefore?: string; status: ("unspecified" | "pending" | "processing" | "completed" | "failed"); maximumConnections?: number; [key: string]: unknown; }; relationships: { origin: { data: { id: string; type: "places"; [key: string]: unknown; }; [key: string]: unknown; }; destination: { data: { id: string; type: "places"; [key: string]: unknown; }; [key: string]: unknown; }; allowedSegmentTypes?: { data: ({ id: string; type: "leg-types"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/loyalty-programs": {
    get: {
      request?: {
        query?: {
          "page[cursor]"?: string;
          "page[limit]"?: number;
          "query[name]"?: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "loyalty-programs"; attributes: { iata: string; airline: string; name: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/trips/searches/{tripSearchId}/trips": {
    get: {
      request: {
        path: {
          tripSearchId: string;
        };
        query?: {
          sort?: "id";
          "page[cursor]"?: string;
          "page[limit]"?: number;
          include?: (("segments" | "segments.legs" | "segments.legs.legType"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "trips"; attributes: { [key: string]: unknown; }; relationships: { segments: { data: ({ id: string; type: "segments"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; included?: ({ id: string; type: "segments"; attributes: { name: string; operator: string; [key: string]: unknown; }; relationships: { legs: { data: ({ id: string; type: "legs"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "legs"; attributes: { departureAt: string; arrivalAt: string; origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "leg-types"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/status/air": {
    get: {
      request: {
        query: {
          carrierCode: string;
          flightNumber: number;
          departureAt: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "flight-status"; attributes: { carrierCode: string; flightNumber: number; departureAt: string; delays: { departureGateDelayMinutes?: number; arrivalGateDelayMinutes?: number; [key: string]: unknown; }; airportInformation: { departureTerminal?: string; departureGate?: string; arrivalTerminal?: string; arrivalGate?: string; baggageBelt?: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/trip-candidates/searches": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "trip-candidate-searches"; attributes: { sessionToken?: string; criteria: ({ origin: { precision?: ("precise" | "area"); [key: string]: unknown; } & { latitude: number; longitude: number; [key: string]: unknown; }; destination: { precision?: ("precise" | "area"); [key: string]: unknown; } & { latitude: number; longitude: number; [key: string]: unknown; }; departureAfter: string; departureBefore?: (string | null); maximumConnections?: number; [key: string]: unknown; })[]; passengers: ({ dateOfBirth: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships?: { allowedSegmentTypes?: { data: ({ id: string; type: "leg-types"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "trip-candidate-searches"; attributes: { expiresAt: string; status: ("unspecified" | "pending" | "processing" | "completed" | "failed"); criteria: ({ origin: { precision?: ("precise" | "area"); [key: string]: unknown; } & { latitude: number; longitude: number; [key: string]: unknown; }; destination: { precision?: ("precise" | "area"); [key: string]: unknown; } & { latitude: number; longitude: number; [key: string]: unknown; }; departureAfter: string; departureBefore?: (string | null); maximumConnections?: number; [key: string]: unknown; })[]; passengers: ({ dateOfBirth: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships?: { allowedSegmentTypes?: { data: ({ id: string; type: "leg-types"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/trip-candidates/searches/{tripCandidateSearchId}": {
    get: {
      request: {
        path: {
          tripCandidateSearchId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "trip-candidate-searches"; attributes: { expiresAt: string; status: ("unspecified" | "pending" | "processing" | "completed" | "failed"); criteria: ({ origin: { precision?: ("precise" | "area"); [key: string]: unknown; } & { latitude: number; longitude: number; [key: string]: unknown; }; destination: { precision?: ("precise" | "area"); [key: string]: unknown; } & { latitude: number; longitude: number; [key: string]: unknown; }; departureAfter: string; departureBefore?: (string | null); maximumConnections?: number; [key: string]: unknown; })[]; passengers: ({ dateOfBirth: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships?: { allowedSegmentTypes?: { data: ({ id: string; type: "leg-types"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/trip-candidates/searches/{tripCandidateSearchId}/offers": {
    get: {
      request: {
        path: {
          tripCandidateSearchId: string;
        };
        query?: {
          sort?: ("id" | "createdAt");
          "page[cursor]"?: string;
          "page[limit]"?: number;
          "filter[groups.options.details.cabinClass][eq]"?: (string)[];
          include?: (("groups" | "groups.details" | "groups.details.legType" | "groups.options" | "groups.options.details" | "groups.options.details.cabinClass" | "groups.options.details.details"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "offers"; attributes: { createdAt?: string; expiresAt: string; [key: string]: unknown; }; relationships: { groups: { data: ({ id: string; type: "offer-groups"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; included?: ({ id: string; type: "offer-groups"; attributes: { [key: string]: unknown; }; relationships: { options: { data: ({ id: string; type: "offer-options"; [key: string]: unknown; })[]; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-offer-group-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; meta?: { providerId?: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-offer-group-details"; attributes: { legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "leg-types"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "offer-options"; attributes: { price: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; conditionalPrices?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; description?: (string | null); includedInTotal?: (boolean | null); [key: string]: unknown; })[]; brandName: string; baggageAllowances: ({ isIncluded: boolean; applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { details: { data: ({ id: string; type: "trip-offer-option-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-offer-option-details"; attributes: { cabinClassName: string; baggageAllowances: ({ isIncluded: boolean; applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; [key: string]: unknown; })[]; amenities: { beverage: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; entertainment: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; food: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; power: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; wifi: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; unlimitedMileage?: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; airConditioner?: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; [key: string]: unknown; }; vehicle?: { imageUrl?: (string | null); model?: (string | null); seatsCount?: (number | null); doorsCount?: (number | null); transmission?: (string | null); fuelType?: (string | null); baggageQuantity?: (number | null); driveType?: (string | null); carClass?: (string | null); [key: string]: unknown; }; [key: string]: unknown; }; relationships: { details: { data: { id: string; type: "trip-offer-group-details"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "cabin-classes"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/orders/{orderId}/messages": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "email-messages"; attributes: { email: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          orderId: string;
        };
      };
      response: ({
        status: 202;
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
          include?: (("journey" | "bookings" | "bookings.details" | "bookings.details.cabinClass" | "bookings.details.legType" | "bookings.bookingCancellation"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { payment: { data: { id: string; type: "payments"; [key: string]: unknown; }; [key: string]: unknown; }; voucher?: { data: { id: string; type: "vouchers"; [key: string]: unknown; }; [key: string]: unknown; }; journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; markup: { data: { id: string; type: "markups"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { included?: ({ id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email?: string; address?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber?: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; operatorBookingReferences: (string)[]; externalReference: string; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details?: { data?: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "cabin-classes"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "leg-types"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "booking-cancellation"; attributes: { status: ("unspecified" | "pending" | "completed" | "rejected" | "no-refund" | "refund-due" | "refund-issued"); [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
  "/orders": {
    get: {
      request?: {
        query?: {
          include?: (("journey" | "bookings" | "bookings.details" | "bookings.details.cabinClass" | "bookings.details.legType" | "bookings.bookingCancellation"))[];
          "page[cursor]"?: string;
          "page[limit]"?: number;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { payment: { data: { id: string; type: "payments"; [key: string]: unknown; }; [key: string]: unknown; }; voucher?: { data: { id: string; type: "vouchers"; [key: string]: unknown; }; [key: string]: unknown; }; journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; markup: { data: { id: string; type: "markups"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; included?: ({ id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; operatorBookingReferences: (string)[]; externalReference: string; rules?: ({ title: string; body: string; [key: string]: unknown; })[]; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; bookingCancellation: { data: { id: string; type: "booking-cancellation"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "cabin-classes"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "leg-types"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "booking-cancellation"; attributes: { status: ("unspecified" | "pending" | "completed" | "rejected" | "no-refund" | "refund-due" | "refund-issued"); [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { attributes: { contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships?: { payment: { data: { id: string; type: "payments"; [key: string]: unknown; }; [key: string]: unknown; }; voucher?: { data: { id: string; type: "vouchers"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { type: "orders"; attributes: { passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { payment: { data: { id: string; type: "payments"; [key: string]: unknown; }; [key: string]: unknown; }; voucher?: { data: { id: string; type: "vouchers"; [key: string]: unknown; }; [key: string]: unknown; }; quote: { data: { id: string; type: "trip-offer-price-quotes"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { payment: { data: { id: string; type: "payments"; [key: string]: unknown; }; [key: string]: unknown; }; voucher?: { data: { id: string; type: "vouchers"; [key: string]: unknown; }; [key: string]: unknown; }; journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; markup: { data: { id: string; type: "markups"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/journeys/{journeyId}/orders": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { attributes: { contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships?: { payment: { data: { id: string; type: "payments"; [key: string]: unknown; }; [key: string]: unknown; }; voucher?: { data: { id: string; type: "vouchers"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { type: "orders"; attributes: { passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { payment: { data: { id: string; type: "payments"; [key: string]: unknown; }; [key: string]: unknown; }; voucher?: { data: { id: string; type: "vouchers"; [key: string]: unknown; }; [key: string]: unknown; }; quote: { data: { id: string; type: "trip-offer-price-quotes"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          journeyId: string;
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { payment: { data: { id: string; type: "payments"; [key: string]: unknown; }; [key: string]: unknown; }; voucher?: { data: { id: string; type: "vouchers"; [key: string]: unknown; }; [key: string]: unknown; }; journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; markup: { data: { id: string; type: "markups"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/orders/markups": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "markups"; attributes: { serviceFee: { currency: string; amount: string; [key: string]: unknown; }; agencyMarkup: { currency: string; amount: string; [key: string]: unknown; }; totalToCollect: { currency: string; amount: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "markups"; attributes: { serviceFee: { currency: string; amount: string; [key: string]: unknown; }; agencyMarkup: { currency: string; amount: string; [key: string]: unknown; }; totalToCollect: { currency: string; amount: string; [key: string]: unknown; }; createdAt: string; updatedAt: string; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/orders/{orderId}/markup": {
    get: {
      request: {
        path: {
          orderId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "markups"; attributes: { serviceFee: { currency: string; amount: string; [key: string]: unknown; }; agencyMarkup: { currency: string; amount: string; [key: string]: unknown; }; totalToCollect: { currency: string; amount: string; [key: string]: unknown; }; createdAt: string; updatedAt: string; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      } | {
        status: 400;
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
  "/simple-offers/searches": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "simple-offer-searches"; attributes: { sessionToken?: string; criteria: { origin: { latitude: number; longitude: number; [key: string]: unknown; }; destination: { latitude: number; longitude: number; [key: string]: unknown; }; departureBefore?: (string | null); departureAfter: string; arrivalBefore?: (string | null); returnDepartureBefore?: (string | null); returnDepartureAfter?: (string | null); [key: string]: unknown; }; passengers: ({ dateOfBirth: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships?: { allowedSegmentTypes?: { data: ({ id: string; type: "leg-types"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "simple-offer-searches"; attributes: { expiresAt: string; status: ("unspecified" | "pending" | "processing" | "completed" | "failed"); criteria: { origin: { latitude: number; longitude: number; [key: string]: unknown; }; destination: { latitude: number; longitude: number; [key: string]: unknown; }; departureBefore?: (string | null); departureAfter: string; arrivalBefore?: (string | null); returnDepartureBefore?: (string | null); returnDepartureAfter?: (string | null); [key: string]: unknown; }; passengers: ({ dateOfBirth: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships?: { allowedSegmentTypes?: { data: ({ id: string; type: "leg-types"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/offers/searches": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "trip-offer-searches"; attributes: { sessionToken?: string; passengers: ({ dateOfBirth: string; [key: string]: unknown; })[]; loyalty?: { airlineIata: string; number: string; firstName: string; lastName: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { trips: { data: ({ id: string; type: "trips"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
        headers?: {
          "Session-Token"?: string;
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "trip-offer-searches"; attributes: { expiresAt: string; passengers: ({ dateOfBirth: string; [key: string]: unknown; })[]; loyalty?: { airlineIata: string; number: string; firstName: string; lastName: string; [key: string]: unknown; }; status: ("unspecified" | "pending" | "processing" | "completed" | "failed"); [key: string]: unknown; }; relationships: { offers: { data: ({ id: string; type: "offers"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/offers/searches/{offerSearchId}": {
    get: {
      request: {
        path: {
          offerSearchId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "trip-offer-searches"; attributes: { expiresAt: string; passengers: ({ dateOfBirth: string; [key: string]: unknown; })[]; loyalty?: { airlineIata: string; number: string; firstName: string; lastName: string; [key: string]: unknown; }; status: ("unspecified" | "pending" | "processing" | "completed" | "failed"); [key: string]: unknown; }; relationships: { offers: { data: ({ id: string; type: "offers"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; included?: ({ id: string; type: "offers"; attributes: { expiresAt: string; [key: string]: unknown; }; relationships: { groups: { data: ({ id: string; type: "offer-groups"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "offer-groups"; attributes: { [key: string]: unknown; }; relationships: { options: { data: ({ id: string; type: "offer-options"; [key: string]: unknown; })[]; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-offer-group-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; meta?: { providerId?: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-offer-group-details"; attributes: { legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "leg-types"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "offer-options"; attributes: { price: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; conditionalPrices?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; description?: (string | null); includedInTotal?: (boolean | null); [key: string]: unknown; })[]; brandName: string; baggageAllowances: ({ isIncluded: boolean; applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { details: { data: ({ id: string; type: "trip-offer-option-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-offer-option-details"; attributes: { cabinClassName: string; baggageAllowances: ({ isIncluded: boolean; applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; [key: string]: unknown; })[]; amenities: { beverage: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; entertainment: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; food: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; power: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; wifi: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; unlimitedMileage?: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; airConditioner?: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; [key: string]: unknown; }; vehicle?: { imageUrl?: (string | null); model?: (string | null); seatsCount?: (number | null); doorsCount?: (number | null); transmission?: (string | null); fuelType?: (string | null); baggageQuantity?: (number | null); driveType?: (string | null); carClass?: (string | null); [key: string]: unknown; }; [key: string]: unknown; }; relationships: { details: { data: { id: string; type: "trip-offer-group-details"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "cabin-classes"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
  "/offers/searches/{offerSearchId}/offers": {
    get: {
      request: {
        path: {
          offerSearchId: string;
        };
        query?: {
          sort?: ("id" | "createdAt");
          "page[cursor]"?: string;
          "page[limit]"?: number;
          "filter[groups.options.details.cabinClass][eq]"?: (string)[];
          include?: (("groups" | "groups.details" | "groups.details.legType" | "groups.options" | "groups.options.details" | "groups.options.details.cabinClass" | "groups.options.details.details"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "offers"; attributes: { createdAt?: string; expiresAt: string; [key: string]: unknown; }; relationships: { groups: { data: ({ id: string; type: "offer-groups"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; included?: ({ id: string; type: "offer-groups"; attributes: { [key: string]: unknown; }; relationships: { options: { data: ({ id: string; type: "offer-options"; [key: string]: unknown; })[]; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-offer-group-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; meta?: { providerId?: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-offer-group-details"; attributes: { legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "leg-types"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "offer-options"; attributes: { price: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; conditionalPrices?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; description?: (string | null); includedInTotal?: (boolean | null); [key: string]: unknown; })[]; brandName: string; baggageAllowances: ({ isIncluded: boolean; applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { details: { data: ({ id: string; type: "trip-offer-option-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-offer-option-details"; attributes: { cabinClassName: string; baggageAllowances: ({ isIncluded: boolean; applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; [key: string]: unknown; })[]; amenities: { beverage: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; entertainment: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; food: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; power: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; wifi: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; unlimitedMileage?: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; airConditioner?: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; [key: string]: unknown; }; vehicle?: { imageUrl?: (string | null); model?: (string | null); seatsCount?: (number | null); doorsCount?: (number | null); transmission?: (string | null); fuelType?: (string | null); baggageQuantity?: (number | null); driveType?: (string | null); carClass?: (string | null); [key: string]: unknown; }; [key: string]: unknown; }; relationships: { details: { data: { id: string; type: "trip-offer-group-details"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "cabin-classes"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; } & { links: { next: string; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/offers/{offerId}": {
    get: {
      request: {
        path: {
          offerId: string;
        };
        query?: {
          include?: (("groups" | "groups.details" | "groups.details.legType" | "groups.options" | "groups.options.details" | "groups.options.details.cabinClass" | "groups.options.details.details"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "offers"; attributes: { expiresAt: string; [key: string]: unknown; }; relationships: { groups: { data: ({ id: string; type: "offer-groups"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; included?: ({ id: string; type: "offers"; attributes: { expiresAt: string; [key: string]: unknown; }; relationships: { groups: { data: ({ id: string; type: "offer-groups"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "offer-groups"; attributes: { [key: string]: unknown; }; relationships: { options: { data: ({ id: string; type: "offer-options"; [key: string]: unknown; })[]; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-offer-group-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; meta?: { providerId?: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-offer-group-details"; attributes: { legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "leg-types"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "offer-options"; attributes: { price: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; conditionalPrices?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; description?: (string | null); includedInTotal?: (boolean | null); [key: string]: unknown; })[]; brandName: string; baggageAllowances: ({ isIncluded: boolean; applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { details: { data: ({ id: string; type: "trip-offer-option-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-offer-option-details"; attributes: { cabinClassName: string; baggageAllowances: ({ isIncluded: boolean; applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; [key: string]: unknown; })[]; amenities: { beverage: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; entertainment: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; food: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; power: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; wifi: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; unlimitedMileage?: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; airConditioner?: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; [key: string]: unknown; }; vehicle?: { imageUrl?: (string | null); model?: (string | null); seatsCount?: (number | null); doorsCount?: (number | null); transmission?: (string | null); fuelType?: (string | null); baggageQuantity?: (number | null); driveType?: (string | null); carClass?: (string | null); [key: string]: unknown; }; [key: string]: unknown; }; relationships: { details: { data: { id: string; type: "trip-offer-group-details"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "cabin-classes"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
  "/offers/quotes": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "trip-offer-price-quotes"; attributes?: { sessionToken?: string; [key: string]: unknown; }; relationships: { offer: { data: { id: string; type: "offers"; [key: string]: unknown; }; [key: string]: unknown; }; options: { data: ({ id: string; type: "offer-options"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 201;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "trip-offer-price-quotes"; attributes?: { expiresAt: string; price: ({ currency: string; amount: string; [key: string]: unknown; } | null | null); priceBreakdown?: (({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[] | null); conditionalPrices?: (({ price: { currency: string; amount: string; [key: string]: unknown; }; description?: (string | null); includedInTotal?: (boolean | null); [key: string]: unknown; })[] | null); penalties: ({ applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; penaltyType: ("exchange" | "refund"); changeable?: boolean; refundable: boolean; conditionsApply?: boolean; applicability: ("before" | "after"); price: ({ currency: string; amount: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; required: (("date-of-birth" | "nationality" | "expiration-date" | "issuing-country" | "passport-number" | "residence-country-code" | "residence-address" | "issue-date"))[]; rules: ({ title: string; body: string; [key: string]: unknown; })[]; status: ("unspecified" | "pending" | "processing" | "completed" | "failed"); [key: string]: unknown; }; relationships: { offer: { data: { id: string; type: "offers"; [key: string]: unknown; }; [key: string]: unknown; }; options: { data: ({ id: string; type: "offer-options"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/offers/quotes/{offerPriceQuoteId}": {
    get: {
      request: {
        path: {
          offerPriceQuoteId: string;
        };
        query?: {
          include?: (("offer" | "offer.groups" | "offer.groups.details" | "offer.groups.details.legType" | "options" | "options.details" | "options.details.cabinClass" | "options.details.details"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "trip-offer-price-quotes"; attributes?: { expiresAt: string; price: ({ currency: string; amount: string; [key: string]: unknown; } | null | null); priceBreakdown?: (({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[] | null); conditionalPrices?: (({ price: { currency: string; amount: string; [key: string]: unknown; }; description?: (string | null); includedInTotal?: (boolean | null); [key: string]: unknown; })[] | null); penalties: ({ applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; penaltyType: ("exchange" | "refund"); changeable?: boolean; refundable: boolean; conditionsApply?: boolean; applicability: ("before" | "after"); price: ({ currency: string; amount: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; required: (("date-of-birth" | "nationality" | "expiration-date" | "issuing-country" | "passport-number" | "residence-country-code" | "residence-address" | "issue-date"))[]; rules: ({ title: string; body: string; [key: string]: unknown; })[]; status: ("unspecified" | "pending" | "processing" | "completed" | "failed"); [key: string]: unknown; }; relationships: { offer: { data: { id: string; type: "offers"; [key: string]: unknown; }; [key: string]: unknown; }; options: { data: ({ id: string; type: "offer-options"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; included?: ({ id: string; type: "offers"; attributes: { expiresAt: string; [key: string]: unknown; }; relationships: { groups: { data: ({ id: string; type: "offer-groups"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "offer-groups"; attributes: { [key: string]: unknown; }; relationships: { options: { data: ({ id: string; type: "offer-options"; [key: string]: unknown; })[]; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-offer-group-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-offer-group-details"; attributes: { legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "offer-options"; attributes: { price: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; conditionalPrices?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; description?: (string | null); includedInTotal?: (boolean | null); [key: string]: unknown; })[]; brandName: string; baggageAllowances: ({ isIncluded: boolean; applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { details: { data: ({ id: string; type: "trip-offer-option-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-offer-option-details"; attributes: { cabinClassName: string; baggageAllowances: ({ isIncluded: boolean; applicableTo: { dateOfBirthAfter: (string | null); dateOfBirthBefore: (string | null); [key: string]: unknown; }; [key: string]: unknown; })[]; amenities: { beverage: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; entertainment: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; food: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; power: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; wifi: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; unlimitedMileage?: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; airConditioner?: { availability: ("unspecified" | "unavailable" | "available" | "included"); [key: string]: unknown; }; [key: string]: unknown; }; vehicle?: { imageUrl?: (string | null); model?: (string | null); seatsCount?: (number | null); doorsCount?: (number | null); transmission?: (string | null); fuelType?: (string | null); baggageQuantity?: (number | null); driveType?: (string | null); carClass?: (string | null); [key: string]: unknown; }; [key: string]: unknown; }; relationships: { details: { data: { id: string; type: "trip-offer-group-details"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "cabin-classes"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
          data: { data?: { id: string; type: "payments"; attributes: { clientSecret: string; ephemeralKey?: string; customerId?: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/payments/{paymentIntentId}": {
    patch: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "payments"; relationships: { voucher?: { data: { id: string; type: "vouchers"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          paymentIntentId: string;
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
      } | {
        status: 404;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/places": {
    get: {
      request?: {
        query?: {
          "query[name]"?: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id?: string; type?: "places"; attributes?: { name: string; latitude: number; longitude: number; countryCode: string; countryName?: (string | null); timeZone: string; iataCode?: (string | null); population?: number; mainCity?: string; [key: string]: unknown; }; relationships?: { types: { data: ({ id: string; type: "place-types"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
  "/places/{placeId}": {
    get: {
      request: {
        path: {
          placeId: string;
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id?: string; type?: "places"; attributes?: { name: string; latitude: number; longitude: number; countryCode: string; countryName?: (string | null); timeZone: string; iataCode?: (string | null); population?: number; mainCity?: string; [key: string]: unknown; }; relationships?: { types: { data: ({ id: string; type: "place-types"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/verification-code": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "verification-codes"; attributes: { email: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
        status: 403;
        body: {
          type: "application/vnd.api+json";
          data: { errors: ({ status: string; title?: string; detail: string; code?: string; source?: { pointer?: string; parameter?: string; header?: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      });
    };
  };
  "/verification-code/{userEmail}": {
    get: {
      request: {
        path: {
          userEmail: string;
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
  };
  "/users": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data: { type: "users"; attributes: { firstName: string; lastName: string; password?: string; email: string; phone: string; [key: string]: unknown; }; relationships?: { guest?: { data: { id: string; type: "guests"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  };
  "/users/sessions": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data?: { type: "user-sessions"; attributes: { password: string; email: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data?: { id: string; type: "user-sessions"; attributes: { [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/users/{userEmail}": {
    patch: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data?: { type: "users"; attributes: { password: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
        path: {
          userEmail: string;
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
  };
  "/users/me": {
    get: {
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "users"; [key: string]: unknown; } & { attributes: { firstName?: string; lastName?: string; email?: string; phone?: string; gender?: ("female" | "male" | "unspecified"); title?: ("mr" | "mrs" | "miss" | "ms"); countryCode?: string; dateOfBirth?: string; loyaltyPrograms?: ({ program: string; number: string; [key: string]: unknown; })[]; createdAt?: string; updatedAt?: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
        query: {
          password: string;
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
          data: { data: { type: "users"; [key: string]: unknown; } & { attributes: { firstName?: string; lastName?: string; email?: string; phone?: string; gender?: ("female" | "male" | "unspecified"); title?: ("mr" | "mrs" | "miss" | "ms"); countryCode?: string; dateOfBirth?: string; loyaltyPrograms?: ({ program: string; number: string; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { data: { type: "users"; attributes: { oldPassword?: string; newPassword?: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "users"; [key: string]: unknown; } & { attributes: { firstName?: string; lastName?: string; email?: string; phone?: string; gender?: ("female" | "male" | "unspecified"); title?: ("mr" | "mrs" | "miss" | "ms"); countryCode?: string; dateOfBirth?: string; loyaltyPrograms?: ({ program: string; number: string; [key: string]: unknown; })[]; createdAt?: string; updatedAt?: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
  "/users/me/preferences": {
    get: {
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id: string; type: "preferences"; attributes: { title: string; ref: string; type: ("boolean" | "integer" | "boolean_collection"); category: string; value: boolean | number | ({ title: string; ref: string; value: boolean; imageUrl: string; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
          data: { data: { type: "preferences"; attributes: { preferences: ({ ref: string; value: boolean | number | ({ ref: string; value: boolean; [key: string]: unknown; })[]; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
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
        status: 404;
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
          include?: (("bookings" | "bookings.order" | "bookings.order.journey" | "bookings.details" | "bookings.details.cabinClass" | "bookings.details.legType"))[];
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: { id: string; type: "cancellation-request"; attributes: { status: ("unspecified" | "pending" | "completed"); [key: string]: unknown; }; relationships: { bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; }; included?: ({ id: string; type: "orders"; attributes: { createdAt: string; passengers: ({ firstName: string; lastName: string; title: ("unspecified" | "mr" | "mrs" | "ms" | "miss"); gender: ("unspecified" | "male" | "female"); dateOfBirth: string; travelerDocument?: ({ documentType?: "passport"; documentNumber?: string; documentIssueCountry?: string; documentExpirationDate?: string; documentIssueDate?: string; nationality?: string; residenceCountryCode?: string; [key: string]: unknown; } | null | null); [key: string]: unknown; })[]; residenceAddress?: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { journey: { data: { id: string; type: "journeys"; [key: string]: unknown; }; [key: string]: unknown; }; bookings: { data: ({ id: string; type: "trip-bookings"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "journeys"; attributes: { createdAt: string; reference: string; contactDetails: { email: string; address: { addressLines: (string)[]; countryCode: string; postalCode: string; city: string; [key: string]: unknown; }; phoneNumber: string; [key: string]: unknown; }; [key: string]: unknown; }; relationships: { orders: { data: ({ id: string; type: "orders"; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-bookings"; attributes: { totalPrice: { currency: string; amount: string; [key: string]: unknown; }; priceBreakdown?: ({ price: { currency: string; amount: string; [key: string]: unknown; }; breakdownType: ("base-fare" | "tax" | "reseller-mark-up" | "company-mark-up" | "service-mark-up"); [key: string]: unknown; })[]; operatorBookingReferences: (string)[]; externalReference: string; rules?: ({ title: string; body: string; [key: string]: unknown; })[]; ticketUrls?: (string)[]; [key: string]: unknown; }; relationships: { order: { data: { id: string; type: "orders"; [key: string]: unknown; }; [key: string]: unknown; }; status: { data: { id: string; type: "booking-statuses"; [key: string]: unknown; }; [key: string]: unknown; }; details: { data: ({ id: string; type: "trip-booking-details"; [key: string]: unknown; })[]; [key: string]: unknown; }; bookingCancellation: { data: { id: string; type: "booking-cancellation"; [key: string]: unknown; }; [key: string]: unknown; } | null; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "trip-booking-details"; attributes: { cabinClassName: string; vendor: string; operator: (string | null); routeIdentifiers: { vendor: string; operator: (string | null); [key: string]: unknown; }; sequences: { trip: number; segment: number; [key: string]: unknown; }; legs: ({ origin: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; destination: { ref: string; name: string; latitude: number; longitude: number; timeZone: string; [key: string]: unknown; }; departureAt: string; arrivalAt: string; [key: string]: unknown; })[]; [key: string]: unknown; }; relationships: { booking: { data: { id: string; type: "trip-bookings"; [key: string]: unknown; }; [key: string]: unknown; }; cabinClass: { data: { id: string; type: "cabin-classes"; [key: string]: unknown; }; [key: string]: unknown; }; legType: { data: { id: string; type: "leg-types"; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "cabin-classes"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; } | { id: string; type: "leg-types"; attributes: { name: string; [key: string]: unknown; }; [key: string]: unknown; } & { links: { self: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
  "/flight-delay-prediction": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data?: ({ attributes?: { flightNumber: string; scheduledDepartureAt: string; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id?: string; type?: "flight-delay-prediction"; attributes?: { flightNumber: string; scheduledDepartureAt: string; delay: number; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
  "/co2-emissions": {
    post: {
      request: {
        body: {
          type: "application/vnd.api+json";
          data: { data?: { attributes?: { flights: ({ origin: string; destination: string; operatingCarrierCode: string; flightNumber: number; departureDate: string; [key: string]: unknown; })[]; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; };
        };
      };
      response: ({
        status: 200;
        body: {
          type: "application/vnd.api+json";
          data: { data: ({ id?: string; type?: "emissions"; attributes?: { flight: { origin: string; destination: string; operatingCarrierCode: string; flightNumber: number; departureDate: string; [key: string]: unknown; }; emissions?: { first?: number; business?: number; premiumEconomy?: number; economy?: number; units?: string; [key: string]: unknown; }; [key: string]: unknown; }; [key: string]: unknown; })[]; [key: string]: unknown; };
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
};
