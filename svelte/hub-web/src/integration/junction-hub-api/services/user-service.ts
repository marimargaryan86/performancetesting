import type { PaginatedData } from "models/common";
import {
  userParser,
  type User,
  type UserSchema,
  type UserProfile,
  type UserProfileSchema,
  userProfileParser,
} from "../schemas/user";
import JunctionHubApiService from "./junction-hub-api-service";
import type { Session } from "integration/ory/schemas";

export default class UserService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
  }: {
    session: Session;
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

  async get({ session, id }: { session: Session; id: string }): Promise<User> {
    const resp = await this.makeRequest<{ data: UserSchema }>(`/users/${id}`, { session });

    return userParser.toModel(resp.json.data);
  }

  async getProfile({ session }: { session: Session }): Promise<UserProfile> {
    const resp = await this.makeRequest<{ data: UserProfileSchema }>("/users/me", { session });

    return userProfileParser.toModel(resp.json.data);
  }
}
