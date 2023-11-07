import type { PaginatedData } from "models/common";
import {
  userParser,
  type User,
  type UserSchema,
  type UserPermissions,
  type UserPermissionsSchema,
} from "../schemas/user";
import JunctionHubApiService from "./junction-hub-api-service";
import type { SessionModel } from "models/user";

export default class UserService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
  }: {
    session: SessionModel;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<User>> {
    const resp = await this.makeRequest<{ data: UserSchema[] }>("/users", {
      session,
      queryParams: { "page[cursor]": cursor, "page[limit]": limit },
    });

    return {
      data: resp.json.data.map(userParser.toModel),
    };
  }

  async get({ session, id }: { session: SessionModel; id: string }): Promise<User> {
    const resp = await this.makeRequest<{ data: UserSchema }>(`/users/${id}`, { session });

    return userParser.toModel(resp.json.data);
  }

  async getOwnPermissions({ session }: { session: SessionModel }): Promise<UserPermissions> {
    const resp = await this.makeRequest<UserPermissionsSchema>("/users/me", { session });

    return resp.json;
  }
}
