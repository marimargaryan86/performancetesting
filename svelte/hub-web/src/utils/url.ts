import type { z } from "zod";
import { get, writable, type Writable } from "svelte/store";
import { browser } from "$app/environment";
import queryStore from "stores/query-store";
import { ensureDefined } from "./array";

export class URLExtended<
  TQuery extends Record<
    TQuerySchema extends z.AnyZodObject ? keyof TQuerySchema["_output"] : string,
    string | number | undefined
  >,
  TQuerySchema extends z.AnyZodObject | undefined = undefined,
  TQuerySchemaOutput = TQuerySchema extends z.AnyZodObject ? TQuerySchema["_output"] : TQuery,
> extends URL {
  private readonly querySchema?: TQuerySchema;
  readonly query: TQuerySchemaOutput;

  constructor(
    url: string | URL,
    options?: {
      base?: string | URL;
      query?: TQuery;
      querySchema?: TQuerySchema;
    },
  ) {
    super(url, options?.base);

    this.querySchema = options?.querySchema;

    if (options?.query) {
      this.setSearchParams(options.query);
      this.query = options.query as unknown as TQuerySchemaOutput;
    } else if (this.querySchema) {
      this.query = this.querySchema.parse(
        Object.fromEntries(this.searchParams.entries()),
      ) as TQuerySchemaOutput;
    } else {
      this.query = {} as TQuerySchemaOutput;
    }
  }

  private setSearchParams(query: Record<string, string | number | undefined>): void {
    Object.entries(query).forEach(([key, val]) => {
      if (val !== undefined) {
        this.searchParams.set(key, val.toString());
      }
    });
  }
}

type Setter<TData> = (value: TData, navigate?: boolean) => void;

/**
 * Creates a query store
 *
 * @param serialize Serialize the store value into a query compatible structure
 * @param deserialize Serialize the url query to a desired format
 * @returns A writable query store
 */
export function createQueryStore<
  TData extends Record<string, unknown>,
  TQuery extends Record<string, string | undefined>,
>(serialize: (data: TData) => TQuery, deserialize: (query: TQuery) => TData): Writable<TData> {
  if (!browser) {
    return writable({} as TData);
  }

  const store = writable<TData>(deserialize(get(queryStore) as TQuery), () =>
    queryStore.subscribe((value) => {
      (store.set as Setter<TData>)(deserialize(value as TQuery), false);
    }),
  );

  const { set } = store;

  store.set = (value: TData, navigate = true): void => {
    if (!navigate) {
      return set(value);
    }

    const serialized = serialize(value);

    queryStore.set(
      Object.fromEntries(
        Object.entries(serialized)
          .map(([key, val]) => (val === undefined ? undefined : [key, val]))
          .filter(ensureDefined),
      ),
    );
  };

  return store;
}
