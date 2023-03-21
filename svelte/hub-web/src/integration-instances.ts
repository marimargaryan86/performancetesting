import config from "config/public-config";
import junctionPay from "integration/junction-pay/services";

export default {
  junctionPay: {
    auth: new junctionPay.AuthenticationService(config.PUBLIC_PAY_ADMIN_API_BASE_URL),
  },
};
