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
    .filter((item): item is [string, string] => Boolean(item));

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
