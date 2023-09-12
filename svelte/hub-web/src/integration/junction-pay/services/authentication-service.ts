import {
  createUserTokenModel,
  userTokenModel,
  type CreateUserTokenModel,
  type UserTokenSchema,
} from "../schemas/auth";
import JunctionPayService from "./junction-pay-service";

export default class AuthenticationService extends JunctionPayService {
  async createToken(data: CreateUserTokenModel): Promise<string> {
    const resp = await this.makeRequest<{ data: UserTokenSchema }>("/users/tokens", {
      method: "POST",
      data: { data: createUserTokenModel.toSchema(data) },
    });

    if (resp.status !== 200) {
      throw new Error(`Junction Pay error: ${resp.status}`);
    }

    return userTokenModel.toModel((await resp.json()).data).token;
  }
}
