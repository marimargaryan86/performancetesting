import integrationInstances from "integration-instances";
import type { LoginForm } from "integration/ory/schemas";

export async function load(event): Promise<{ loginFlow: LoginForm }> {
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
