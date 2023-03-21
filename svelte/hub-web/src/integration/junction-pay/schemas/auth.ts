export interface CreateAuthTokenResponse {
  data: {
    type: "user-tokens";
    id: string;
    attributes: {
      token: string;
    };
  };
}
