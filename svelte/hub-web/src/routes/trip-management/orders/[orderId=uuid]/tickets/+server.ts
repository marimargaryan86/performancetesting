import { getTicketsZip } from "utils/ticket-manager.server";

export async function GET(event): Promise<Response> {
  const { orderId } = event.params;

  try {
    const zip = await getTicketsZip({ session: event.locals.session, orderId });

    return new Response(zip.data, {
      status: 200,
      headers: {
        "content-type": "application/zip",
        "content-disposition": `attachment; filename=${zip.name}`,
      },
    });
  } catch {
    return new Response(undefined, { status: 404 });
  }
}
