import { fail, type ActionFailure, redirect } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import routeConfig from "routeConfig";

export const actions = {
  async login(event): Promise<void | ActionFailure<{
    unauthorized?: boolean;
    email?: string | boolean;
    password?: string;
  }>> {
    const formData = await event.request.formData();
    const email = formData.get("email")?.toString().trim() as string;
    const password = formData.get("password")?.toString() as string;

    const errors = {
      email: email?.length ? undefined : "Please enter your e-mail",
      password: password?.length ? undefined : "Please enter your password",
    };

    if (Object.values(errors).filter(Boolean).length) {
      return fail(422, errors);
    }

    try {
      const token = await integrationInstances.junctionPayApi.auth.createToken({
        email,
        password,
      });

      event.cookies.set("session-token", token, { path: "/" });
    } catch {
      return fail(401, {
        unauthorized: true,
        email: true,
        password: "Email/Username & Password not recognised. Please correct and try again.",
      });
    }

    throw redirect(303, routeConfig.home);
  },
  logout(event): void {
    event.cookies.delete("session-token", { path: "/" });

    throw redirect(303, routeConfig.login);
  },
};
