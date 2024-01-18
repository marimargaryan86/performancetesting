import type { z } from "zod";

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
