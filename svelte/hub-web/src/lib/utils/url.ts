export class URLExtended extends URL {
  private _query: Record<string, unknown> = {};

  get query(): Record<string, unknown> {
    return this._query;
  }

  set query(data: Record<string, unknown>) {
    this._query = data;
    this.setSearchParams(data);
  }

  constructor(
    url: string | URL,
    options?: {
      base?: string | URL;
      query?: Record<string, unknown>;
    },
  ) {
    super(url, options?.base);

    if (options?.query) {
      this.query = options.query;
    }
  }

  private setSearchParams(query: Record<string, unknown>): void {
    Object.entries(query).forEach(([key, val]) => {
      if (val !== undefined && val !== null) {
        this.searchParams.set(key, val.toString());
      }
    });
  }
}
