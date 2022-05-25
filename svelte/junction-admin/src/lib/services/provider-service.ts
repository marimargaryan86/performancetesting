import type { ProviderModel, ProviderSearchData } from "$lib/models/provider";
import utils from "$lib/utils";
import BaseService from "./base-service";
import mock from "./mock";

export default class ProviderService extends BaseService {
  async find(data?: ProviderSearchData, pageOffset = 0, pageLimit = 50): Promise<ProviderModel[]> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (data?.name === "asd" || pageOffset === 5) {
      throw new Error("NO_PROVIDERS_FOUND");
    }

    return [...Array(pageLimit)].map(() => mock.generateProvider());
  }

  async get(providerId: string): Promise<ProviderModel> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (providerId === "00000000-0000-0000-0000-000000000000") {
      throw new Error("PROVIDER_NOT_FOUND");
    }

    return { ...mock.generateProvider(), id: providerId };
  }
}
