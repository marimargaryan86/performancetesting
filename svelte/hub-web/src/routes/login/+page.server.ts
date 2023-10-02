import { fail, type ActionFailure, redirect } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { LoginFormModel } from "integration/ory/schemas";
import routeConfig from "routeConfig";
import { deleteSession, setSession } from "utils/auth";
import { getActionRequestJsonData } from "utils/common";
import { z } from "zod";

export async function load(event): Promise<{ loginFlow: LoginFormModel }> {
  const loginForm = await integrationInstances.ory.getLoginForm();

  loginForm.cookies.forEach((cookie) =>
    event.cookies.set(cookie.name, cookie.value, {
      expires: cookie.expires,
      httpOnly: cookie.httpOnly,
      maxAge: cookie.maxAge,
      path: "/",
      priority: cookie.priority,
      sameSite: cookie.sameSite,
      secure: cookie.secure,
    }),
  );

  return { loginFlow: loginForm.form };
}

const loginActionData = z.object({
  id: z.string().uuid(),
  data: z.record(z.string()),
});
export type LoginActionData = z.infer<typeof loginActionData>;

export const actions = {
  async login(event): Promise<void | ActionFailure<{ unauthorized: boolean }>> {
    try {
      const data = await getActionRequestJsonData(event, loginActionData);
      const session = await integrationInstances.ory.authenticate({
        cookies: event.cookies.getAll(),
        data: data.data,
        flowId: data.id,
      });

      setSession(session.id, session.token, event);
    } catch {
      return fail(401, { unauthorized: true });
    }
  },
  logout(event): void {
    deleteSession(event);

    throw redirect(303, routeConfig.routes.login.root);
  },
};
