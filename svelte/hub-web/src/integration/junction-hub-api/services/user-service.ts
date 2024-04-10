import type { PaginatedData } from "$lib/models/common";
import {
  userParser,
  type User,
  type UserSchema,
  type UserProfile,
  type UserProfileSchema,
  userProfileParser,
  type UserPut,
} from "../schemas/user";
import JunctionHubApiService from "./junction-hub-api-service";
import type * as OrySchemas from "~/integration/ory/schemas";

export default class UserService extends JunctionHubApiService {
  async find({
    session,
    cursor,
    limit = 100,
  }: {
    session: OrySchemas.Session;
    cursor?: string;
    limit?: number;
  }): Promise<PaginatedData<User>> {
    const resp = await this.makeRequest<{ data: UserSchema[]; links: { next: string } }>("/users", {
      session,
      queryParams: { "page[cursor]": cursor, "page[limit]": limit },
    });

    return {
      data: resp.json.data.map(userParser.toModel),
      cursor: UserService.getCursor(resp.json),
    };
  }

  async get({ session, id }: { session: OrySchemas.Session; id: string }): Promise<User> {
    const resp = await this.makeRequest<{ data: UserSchema }>(`/users/${id}`, { session });

    return userParser.toModel(resp.json.data);
  }

  async create({ session, data }: { session: OrySchemas.Session; data: UserPut }): Promise<User> {
    const resp = await this.makeRequest<{ data: UserSchema }>("/users", {
      session,
      method: "POST",
      data: { data: userParser.toPutSchema(data) },
    });

    return userParser.toModel(resp.json.data);
  }

  async update({
    session,
    id,
    data,
  }: {
    session: OrySchemas.Session;
    data: UserPut;
    id: string;
  }): Promise<User> {
    const resp = await this.makeRequest<{ data: UserSchema }>(`/users/${id}`, {
      session,
      method: "PATCH",
      data: { data: userParser.toPutSchema(data) },
    });

    return userParser.toModel(resp.json.data);
  }

  async getProfile({ session }: { session: OrySchemas.Session }): Promise<UserProfile> {
    const resp = await this.makeRequest<{ data: UserProfileSchema }>("/users/me", { session });

    return userProfileParser.toModel(resp.json.data);
  }

  async remove({ session, id }: { session: OrySchemas.Session; id: string }): Promise<void> {
    await this.makeRequest(`/users/${id}`, { session, method: "DELETE" });
  }
}
