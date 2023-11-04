export type RouteIdentifiers = {
  vendor: string;
  operator?: string;
};

export type RouteIdentifiersSchema = {
  vendor: string;
  operator: string | null;
};

export const routeIdentifiersParser = {
  toModel: (data: RouteIdentifiersSchema): RouteIdentifiers => ({
    vendor: data.vendor,
    operator: data.operator ?? undefined,
  }),
};
