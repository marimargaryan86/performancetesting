import { dev } from "$app/environment";
import { env } from "$env/dynamic/private";
import integrationInstances from "integration-instances";
import type { LoginFlow } from "integration/ory/schemas/login-flow";
import jwt from "jsonwebtoken";

const COOKIE_OPTIONS = {
  path: "/",
  httpOnly: true,
  secure: !dev,
};

export async function load(event): Promise<{ flow: LoginFlow }> {
  const { flow, cookies } = await integrationInstances.ory.loginFlow.create();

  event.cookies.set("login-token", jwt.sign(cookies, env.JWT_SECRET ?? "secret"), COOKIE_OPTIONS);

  return { flow };
}
