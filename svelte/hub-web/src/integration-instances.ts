import config from "config/public-config";
import AuthService from "integration/services/auth-service";

export default {
  auth: new AuthService(config.PUBLIC_PAY_ADMIN_API_BASE_URL),
};
