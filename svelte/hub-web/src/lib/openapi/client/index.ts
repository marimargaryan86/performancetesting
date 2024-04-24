import { ensureDefined } from "../resolvers/helpers";
import type * as Generated from "./types/generated";
import type { Fetch, FetchHeadersInit, FetchParams, FetchRequestInit } from "./types";
import objectExt from "$lib/object-ext";

function getUrl(resource: string, baseUrl: string, params?: FetchParams): URL {
  let finalResource = resource;

  if (params?.path) {
    // Replace path parameters
    objectExt.entries(params.path).forEach(([name, val]) => {
      finalResource = finalResource.replaceAll(`{${name}}`, `${val}`);
    });
  }

  const url = new URL(finalResource, baseUrl);

  if (params?.query) {
    // Add query parameters
    objectExt.entries(params.query).forEach(([name, val]) => {
      if (val !== undefined) {
        url.searchParams.set(name, `${val}`);
      }
    });
  }

  return url;
}

function getHeaders(headers?: FetchHeadersInit): HeadersInit {
  const finalHeaders: HeadersInit = {};

  if (headers) {
    const { "content-type": contentType, accept, cookie, ...rest } = headers;

    if (accept) {
      finalHeaders.accept = accept;
    }

    if (contentType) {
      finalHeaders["content-type"] = contentType;
    }

    if (cookie !== undefined) {
      const parsedCookie = objectExt
        .entries(cookie)
        .map(([name, val]) => (val === undefined ? undefined : `${name}=${val}`))
        .filter(ensureDefined)
        .join("; ");

      if (parsedCookie.length) {
        finalHeaders.cookie = parsedCookie;
      }
    }

    objectExt.entries(rest).forEach(([name, val]) => (finalHeaders[name] = `${val}`));
  }

  return finalHeaders;
}

export function getFetch<TSpecification extends Generated.Specification>({
  baseUrl,
  fetch: fetchFunc = fetch,
}: {
  baseUrl: string;
  fetch?: typeof fetch;
}): Fetch<TSpecification> {
  return ((
    { resource, ...params }: { resource: string } & FetchParams,
    { method, headers, body, ...init }: FetchRequestInit = {},
  ) => {
    const finalInit: RequestInit = {
      ...init,
      headers: getHeaders(headers),
    };

    if (body) {
      finalInit.body = JSON.stringify(body);
    }

    if (method) {
      finalInit.method = method;
    }

    return fetchFunc(getUrl(resource, baseUrl, params), finalInit);
  }) as Fetch<TSpecification>;
}
