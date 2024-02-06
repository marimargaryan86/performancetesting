import { getCookiesFromHeaders } from "~/utils/cookies";
import OryService from "./ory-service";
import {
  settingsFlowParser,
  type SettingsFlow,
  type SettingsFlowSchema,
} from "../schemas/settings-flow";
import type { Session } from "../schemas/authentication";

export default class SettingsFlowService extends OryService {
  async create({
    session,
  }: {
    session: Session;
  }): Promise<{ cookies: Record<string, string>; flow: SettingsFlow }> {
    const resp = await this.makeRequest<SettingsFlowSchema>("/self-service/settings/browser", {
      cookies: { [session.id]: session.token },
    });

    if (resp.status !== 200) {
      throw new Error("An unexpected error occurred");
    }

    return {
      cookies: Object.fromEntries(
        getCookiesFromHeaders(resp.headers).map(({ name, value }) => [name, value]),
      ),
      flow: settingsFlowParser.toModel(resp.json),
    };
  }

  async get({
    id,
    session,
    cookies,
  }: {
    id: string;
    session: Session;
    cookies: Record<string, string>;
  }): Promise<{ cookies: Record<string, string>; flow: SettingsFlow }> {
    const resp = await this.makeRequest<SettingsFlowSchema>("/self-service/settings/flows", {
      queryParams: { id },
      cookies: { ...cookies, [session.id]: session.token },
    });

    if (resp.status !== 200) {
      throw new Error("An unexpected error occurred");
    }

    return {
      cookies: Object.fromEntries(
        getCookiesFromHeaders(resp.headers).map(({ name, value }) => [name, value]),
      ),
      flow: settingsFlowParser.toModel(resp.json),
    };
  }

  async complete({
    id,
    session,
    data,
    cookies,
  }: {
    id: string;
    session: Session;
    data: Record<string, string>;
    cookies: Record<string, string>;
  }): Promise<SettingsFlow> {
    const resp = await this.makeRequest<SettingsFlowSchema>("/self-service/settings", {
      queryParams: { flow: id },
      cookies: { ...cookies, [session.id]: session.token },
      data,
      method: "POST",
    });

    try {
      return settingsFlowParser.toModel(resp.json);
    } catch {
      throw new Error("An unexpected error occurred");
    }
  }
}
