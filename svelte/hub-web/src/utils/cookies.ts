import { ensureDefined } from "./array";

export function getCookie(name: string): string | undefined {
  if (typeof window === "undefined") {
    return undefined;
  }

  const cookies = document.cookie
    .split(";")
    .map((item) => {
      const value = item.trim();
      const match = value.match(/^(?<key>.+?)=(?<val>.+)$/);
      const [key, val] = [match?.groups?.key, match?.groups?.val];

      if (key && val) {
        return [key, val];
      }

      return undefined;
    })
    .filter(ensureDefined);

  return cookies.find(([key]) => key === name)?.[1];
}

export function deleteCookie(name: string): void {
  if (typeof window === "undefined") {
    return;
  }

  document.cookie = `${name}=; max-age=0; path=/`;
}

export function setCookie(name: string, value: string): void {
  if (typeof window === "undefined") {
    return;
  }

  document.cookie = `${name}=${value}; path=/`;
}

export type Cookie = {
  name: string;
  value: string;
  path?: string;
  domain?: string;
  maxAge?: number;
  httpOnly?: boolean;
  secure?: boolean;
  expires?: Date;
  sameSite?: "strict" | "lax" | "none";
  priority?: "low" | "medium" | "high";
};

export function getCookieAttributes(cookieString: string): [key: string, val: string | boolean][] {
  return cookieString
    .split("; ")
    .map<[key: string, val: string | boolean] | undefined>((keyValue) => {
      const match = keyValue.match(/^(?<key>.+?)=(?<val>.+)$|^(?<key2>.+)$/);

      if (match?.groups) {
        if (match.groups.key && match.groups.val) {
          return [match.groups.key, match.groups.val];
        } else if (match.groups.key2) {
          return [match.groups.key2, true];
        }
      }

      return undefined;
    })
    .filter(ensureDefined);
}

export function getCookiesFromHeaders(headers: Headers): Cookie[] {
  const cookieHeader = headers.get("set-cookie");

  if (!cookieHeader) {
    return [];
  }

  const result: Cookie[] = [];
  const cookieStrings = cookieHeader.split(", ");

  cookieStrings.forEach((cookieString) => {
    const attributes = getCookieAttributes(cookieString);
    const [name, ...restAttributes] = attributes;

    if (name) {
      const maxAge = restAttributes.find((attr) => attr[0] === "Max-Age")?.[1];
      const expires = restAttributes.find((attr) => attr[0] === "Expires")?.[1].toString();

      result.push({
        name: name[0],
        value: name[1].toString(),
        path: restAttributes.find((attr) => attr[0] === "Path")?.[1].toString(),
        domain: restAttributes.find((attr) => attr[0] === "Domain")?.[1].toString(),
        maxAge: maxAge ? Number(maxAge) : undefined,
        httpOnly: Boolean(restAttributes.find((attr) => attr[0] === "HttpOnly")?.[1]),
        secure: Boolean(restAttributes.find((attr) => attr[0] === "Secure")?.[1]),
        expires: expires ? new Date(expires) : undefined,
        sameSite: restAttributes
          .find((attr) => attr[0] === "SameSite")?.[1]
          .toString()
          .toLowerCase() as Cookie["sameSite"],
        priority: restAttributes
          .find((attr) => attr[0] === "Priority")?.[1]
          .toString()
          .toLocaleLowerCase() as Cookie["priority"],
      });
    }
  });

  return result;
}
