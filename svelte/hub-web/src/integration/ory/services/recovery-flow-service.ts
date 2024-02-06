import { getCookiesFromHeaders } from "~/utils/cookies";
import {
  recoveryFlowParser,
  type RecoveryFlow,
  type RecoveryFlowSchema,
} from "../schemas/recovery-flow";
import OryService from "./ory-service";
import type { Session } from "../schemas/authentication";

export default class RecoveryFlowService extends OryService {
  async create(): Promise<{ cookies: Record<string, string>; flow: RecoveryFlow }> {
    const resp = await this.makeRequest<RecoveryFlowSchema>("/self-service/recovery/browser");

    if (resp.status !== 200) {
      throw new Error("An unexpected error occurred");
    }

    return {
      cookies: Object.fromEntries(
        getCookiesFromHeaders(resp.headers).map(({ name, value }) => [name, value]),
      ),
      flow: recoveryFlowParser.toModel(resp.json),
    };
  }

  async get({
    id,
    cookies,
  }: {
    id: string;
    cookies: Record<string, string>;
  }): Promise<{ cookies: Record<string, string>; flow: RecoveryFlow }> {
    const resp = await this.makeRequest<RecoveryFlowSchema>("/self-service/recovery/flows", {
      queryParams: { id },
      cookies,
    });

    if (resp.status !== 200) {
      throw new Error("An unexpected error occurred");
    }

    return {
      cookies: Object.fromEntries(
        getCookiesFromHeaders(resp.headers).map(({ name, value }) => [name, value]),
      ),
      flow: recoveryFlowParser.toModel(resp.json),
    };
  }

  async complete({
    id,
    data,
    cookies,
  }: {
    id: string;
    data: Record<string, string>;
    cookies: Record<string, string>;
  }): Promise<{ completed: true; session: Session } | { completed: false; flow: RecoveryFlow }> {
    const resp = await this.makeRequest<RecoveryFlowSchema>("/self-service/recovery", {
      queryParams: { flow: id },
      cookies,
      data,
      method: "POST",
    });

    const respCookies = getCookiesFromHeaders(resp.headers);
    const sessionCookie = respCookies.find((cookie) => cookie.name.startsWith("ory_session"));

    if (resp.status === 422 && sessionCookie) {
      return { completed: true, session: { id: sessionCookie.name, token: sessionCookie.value } };
    }

    try {
      return { completed: false, flow: recoveryFlowParser.toModel(resp.json) };
    } catch {
      throw new Error("An unexpected error occurred");
    }
  }
}
