import type * as CommonSchemas from "~/integration/common/schemas";

export type SearchType = Extract<CommonSchemas.TransportType, "car" | "rail">;

export function match(type: string): type is SearchType {
  return type === "car" || type === "rail";
}
