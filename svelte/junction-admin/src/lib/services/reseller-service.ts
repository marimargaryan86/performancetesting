import type { ResellerModel, ResellerSearchData } from "$lib/models/reseller";
import utils from "$lib/utils";
import BaseService from "./base-service";
import mock from "./mock";

export default class ResellerService extends BaseService {
  async find(data?: ResellerSearchData, pageOffset = 0, pageLimit = 50): Promise<ResellerModel[]> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (data?.name === "asd" || pageOffset === 5) {
      throw new Error("NO_RESELLERS_FOUND");
    }

    return [...Array(pageLimit)].map(() => mock.generateReseller());
  }

  async get(resellerId: string): Promise<ResellerModel> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (resellerId === "00000000-0000-0000-0000-000000000000") {
      throw new Error("RESELLER_NOT_FOUND");
    }

    return { ...mock.generateReseller(), id: resellerId };
  }
}
