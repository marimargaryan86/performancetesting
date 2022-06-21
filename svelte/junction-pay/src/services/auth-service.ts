import utils from "$lib/utils";
import type { UserModel } from "$models/auth-models";
import BaseService from "./base-service";

export default class AuthService extends BaseService {
  async login(username: string, password: string): Promise<UserModel> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (!(username === "asd@asd.asd" && password === "asd")) {
      throw new Error("Invalid credentials");
    }

    return { id: "00000000-0000-0000-0000-000000000000", username: "asd@asd.asd" };
  }

  async logout(): Promise<void> {
    // TODO: Impl.
    await utils.sleep(1500);
  }
}
