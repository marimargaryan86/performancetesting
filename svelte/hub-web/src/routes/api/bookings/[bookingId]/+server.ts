import integrationInstancesServer from "integration-instances-server";
import type { RequestEvent } from "./$types";

export async function GET(event: RequestEvent): Promise<Response> {
  try {
    const order = await integrationInstancesServer.junctionClientApi.bookings.getBooking(
      event.params.bookingId,
    );

    return new Response(JSON.stringify(order), { headers: { "Content-Type": "application/json" } });
  } catch {
    return new Response(undefined, { status: 404 });
  }
}
