import type { Translator } from "$lib/i18n";
import type * as HubSchemas from "~/integration/junction-hub-api/schemas";

export function getBookingStatusOptionFormatter(
  translator: Translator,
): (status?: HubSchemas.BookingStatus, selected?: boolean) => string | undefined {
  return (status, selected) => {
    if (!status) {
      return selected ? undefined : translator("words.none");
    }

    return translator(`statuses.${status}`);
  };
}
