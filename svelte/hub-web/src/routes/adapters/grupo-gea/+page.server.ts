import { dev } from "$app/environment";
import routeConfig from "$lib/route-config";
import { HUB_URL_COOKIE_NAME } from "./+page.svelte";

export function load(event): { url: string } {
  let url = event.cookies.get(HUB_URL_COOKIE_NAME);

  if (!url) {
    url = `${event.url.origin}${routeConfig.routes.tripManagement.routes.book.routes.rail.root}`;
    event.cookies.set(HUB_URL_COOKIE_NAME, url, {
      secure: !dev,
      httpOnly: false,
      path: "/",
      sameSite: dev ? "lax" : "none",
    });
  }

  return {
    url,
  };
}
