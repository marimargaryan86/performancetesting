import type {
  OrderDetailedModel,
  OrderItemModel,
  OrderModel,
  OrderSearchData,
  TripModel,
} from "$lib/models/order";
import utils from "$lib/utils";
import BaseService from "./base-service";
import mock from "./mock";

export default class OrderService extends BaseService {
  async get(orderId: string): Promise<OrderModel> {
    // TODO: Impl.
    await utils.sleep(1500);

    return { ...mock.generateOrder(), id: orderId };
  }

  async getDetailed(orderId: string): Promise<OrderDetailedModel> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (orderId === "00000000-0000-0000-0000-000000000000") {
      throw new Error("ORDER_NOT_FOUND");
    }

    return { ...mock.generateOrderDetailed(), id: orderId };
  }

  async find(data?: OrderSearchData, pageOffset = 0, pageLimit = 50): Promise<OrderModel[]> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (data?.spnr === "asd" || pageOffset === 5) {
      throw new Error("NO_ORDERS_FOUND");
    }

    return [...Array(pageLimit)].map(() => mock.generateOrder());
  }

  async getOrderItem(orderId: string, orderItemId: string): Promise<OrderItemModel> {
    // TODO: impl.
    await utils.sleep(1500);

    if (orderItemId === "00000000-0000-0000-0000-000000000000") {
      throw new Error("ORDER_ITEM_NOT_FOUND");
    }

    const order = { ...mock.generateOrderDetailed(), id: orderId };

    return { ...order.items[0], id: orderItemId };
  }

  async getOrderTrip(
    orderId: string,
    orderItemId: string,
    orderTripId: string,
  ): Promise<TripModel> {
    // TODO: Impl.
    await utils.sleep(1500);

    if (orderTripId === "00000000-0000-0000-0000-000000000000") {
      throw new Error("ORDER_ITEM_NOT_FOUND");
    }

    const order = { ...mock.generateOrderDetailed(), id: orderId };
    const orderItem = { ...order.items[0], id: orderItemId };

    return { ...orderItem.trips[0], id: orderTripId };
  }
}
