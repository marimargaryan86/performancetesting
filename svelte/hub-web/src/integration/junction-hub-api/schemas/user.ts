export type UserPermissions = UserPermissionsSchema;

export type UserPermissionsSchema = {
  permissions: {
    "*"?: object;
    "journey.view"?: object;
    "order.view"?: object;
    "booking.view"?: object;
    "cancel.*"?: object;
    "refund.*"?: object;
    "transaction.*"?: object;
    "journey.*"?: {
      "attributes.resellerId": ["~", string[]];
    };
    "order.*"?: {
      "attributes.resellerId": ["~", string[]];
    };
    "booking.*"?: {
      "attributes.resellerId": ["~", string[]];
    };
    "cancel.add"?: {
      "attributes.resellerId": ["~", string[]];
    };
    "cancel.view"?: {
      "attributes.resellerId": ["~", string[]];
    };
    "refund.view"?: {
      "attributes.resellerId": ["~", string[]];
    };
    "user.*"?: {
      "attributes.resellerId": ["~", string[]];
    };
  };
};

export type User = {
  id: string;
};

export type UserSchema = {
  id: string;
  type: "users";
  attributes: unknown;
};

export const userParser = {
  toModel: (data: UserSchema): User => ({
    id: data.id,
  }),
};
