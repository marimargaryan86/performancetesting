import ResponseError from "integration/response-error";
import type { CreateAuthTokenResponse } from "integration/schemas/auth";
import BaseService from "./base-service";

export default class AuthService extends BaseService {
  async createToken(data: { email: string; password: string }): Promise<string> {
    const result = await this.post("/users/tokens", {
      data: {
        type: "user-tokens",
        attributes: {
          email: data.email,
          password: data.password,
        },
      },
    });

    switch (result.status) {
      case 200:
        return ((await result.json()) as CreateAuthTokenResponse).data.attributes.token;
      case 400:
        throw new ResponseError(await result.json());
      case 404:
        throw new ResponseError(await result.json());
      default:
        throw new Error(`An unexpected error occured: ${result.status}`);
    }
  }
}
