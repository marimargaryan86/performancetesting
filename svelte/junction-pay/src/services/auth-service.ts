import utils from "$lib/utils";
import type { AuthenticationData, UserModel } from "$models/auth-models";
import type { ValidationError } from "$models/common-models";
import BaseService from "./base-service";

export default class AuthService extends BaseService {
  private validateAuthenticationData(
    data: Partial<AuthenticationData>,
  ): [boolean, ValidationError<AuthenticationData>] {
    const errors: ValidationError<AuthenticationData> = {
      email: !data.email?.trim().length ? ["Email missing"] : undefined,
      password: !data.password?.trim().length ? ["Password missing"] : undefined,
    };

    return [this.containsNoErrors(errors), errors];
  }

  async login(data: Partial<AuthenticationData>): Promise<UserModel> {
    const [valid, errors] = this.validateAuthenticationData(data);

    if (!valid) {
      throw errors;
    }

    // TODO: Impl.
    await utils.sleep(1500);

    if (!(data.email === "asd@asd.asd" && data.password === "asd")) {
      throw {
        email: ["Invalid credentials"],
        password: ["Invalid credentials"],
      } as ValidationError<AuthenticationData>;
    }

    return { id: "00000000-0000-0000-0000-000000000000", username: data.email };
  }

  async logout(): Promise<void> {
    // TODO: Impl.
    await utils.sleep(1500);
  }

  async recoverPassword(email: string): Promise<void> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (email === "asd@asd.asd") {
      throw new Error("An unexpected error occured");
    }
  }

  async updatePassword(code: string, password: string) {
    // TODO: Impl.
    await utils.sleep(1500);

    if (password === "asd" || code.length === 0) {
      throw new Error("An unexpected error occured");
    }
  }
}
