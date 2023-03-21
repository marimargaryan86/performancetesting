import type { CreateAuthTokenResponse } from "../schemas/auth";
import JunctionPayService from "./junction-pay-service";

export default class AuthenticationService extends JunctionPayService {
  async createToken(data: { email: string; password: string }): Promise<string> {
    const resp = await fetch(this.getResourceUrl("/users/tokens"), {
      method: "POST",
      body: JSON.stringify({
        data: {
          type: "user-tokens",
          attributes: {
            email: data.email,
            password: data.password,
          },
        },
      }),
      headers: this.headers,
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    return ((await resp.json()) as CreateAuthTokenResponse).data.attributes.token;
  }
}
