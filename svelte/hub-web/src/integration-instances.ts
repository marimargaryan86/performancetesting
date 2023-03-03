import { env } from "$env/dynamic/public";
import AuthService from "integration/services/auth-service";

export default {
  auth: new AuthService(env.PUBLIC_PAY_ADMIN_API_BASE_URL),
};
