export interface UserTokenIdentifierSchema {
  id: string;
  type: "user-tokens";
}

export interface UserTokenSchema extends UserTokenIdentifierSchema {
  attributes: {
    token: string;
  };
}

export type CreateAuthTokenResponseSchema = {
  data: UserTokenSchema;
};
