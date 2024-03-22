import type { RouteParams } from "../$types.js";

/** @type {import('./$types').PageServerLoad} */
export function load({ params }): Promise<{ test: string; params: RouteParams }> {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ test: "test", params });
    }, 5000);
  });
}
