import type { RequestEvent } from "@sveltejs/kit";

export function getPagination(event: RequestEvent): { limit?: number; cursor?: string } {
  const cursor = event.url.searchParams.get("cursor")?.toString();
  const limitStr = event.url.searchParams.get("limit")?.toString();

  return { limit: limitStr ? Number(limitStr) : undefined, cursor };
}
