/** @type {import('./$types').PageServerLoad} */
export function load({ url }): { searchParamsObj: Record<string, string> } {
  const queryParams = url.searchParams;
  const searchParams = Array.from(queryParams.entries());
  const searchParamsObj = Object.fromEntries(searchParams);

  return { searchParamsObj };
}
