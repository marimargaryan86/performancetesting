import integrationInstances from "integration-instances";
import JSZip from "jszip";
import { extension } from "mime-types";
import { ensureDefined } from "utils/array";
import type { SessionModel } from "models/user";

type TicketsZipParams = {
  session: SessionModel;
  orderId: string;
  bookingId?: string;
};

export async function getTicketsZip({ session, orderId, bookingId }: TicketsZipParams): Promise<{
  data: Uint8Array;
  name: string;
}> {
  const order = await integrationInstances.junctionHubApi.orders.get({
    session,
    id: orderId,
  });
  const bookings = bookingId
    ? order.bookings.filter((item) => item.id === bookingId)
    : order.bookings;
  const bookingNo = bookingId
    ? order.bookings.findIndex((item) => item.id === bookingId) + 1
    : undefined;

  const ticketUrls = Array.from(
    new Set(bookings.flatMap((booking) => booking.ticketUrls).filter(ensureDefined)),
  );
  const reference = order.journey?.reference;

  const responses = (
    await Promise.all(
      ticketUrls.map((url) =>
        fetch(url)
          .then((resp) => resp)
          .catch(() => undefined),
      ),
    )
  ).filter(ensureDefined);

  const files = await Promise.all(
    responses.map((resp) =>
      resp.arrayBuffer().then((data) => ({
        type: resp.headers.get("content-type") ?? "application/pdf",
        data,
      })),
    ),
  );

  const zip = new JSZip();

  files.forEach((file, idx) => zip.file(`ticket_${idx + 1}.${extension(file.type)}`, file.data));

  return {
    name: [
      "tickets",
      reference ? `_${reference}` : "",
      bookingNo ? `_booking_${bookingNo}` : "",
      ".zip",
    ].join(""),
    data: await zip.generateAsync({ type: "uint8array" }),
  };
}
