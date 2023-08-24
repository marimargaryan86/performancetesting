export class URLExtended extends URL {
  constructor(url: string | URL, base?: string | URL, query?: Record<string, unknown>) {
    super(url, base);

    if (query) {
      Object.entries(query)
        .filter(([, val]) => Boolean(val ?? false))
        .forEach(([key, val]) => {
          this.searchParams.set(key, `${val}`);
        });
    }
  }
}
