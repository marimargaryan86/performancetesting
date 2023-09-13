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

    return userTokenModel.toModel(resp.json.data).token;
  }
}
