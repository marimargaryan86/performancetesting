import type { CreateAuthTokenResponseSchema } from "../schemas/auth";
import JunctionPayService from "./junction-pay-service";

export default class AuthenticationService extends JunctionPayService {
  async createToken(data: { email: string; password: string }): Promise<string> {
    const resp = await this.makeRequest("/users/tokens", {
      method: "POST",
      data: {
        data: {
          type: "user-tokens",
          attributes: {
            email: data.email,
            password: data.password,
          },
        },
      },
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    return ((await resp.json()) as CreateAuthTokenResponseSchema).data.attributes.token;
  }
}
