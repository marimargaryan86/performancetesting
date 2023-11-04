import { type ActionFailure, fail } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import { ensureJunctionError } from "integration/common/junction-error";
import type { CancellationRequest } from "integration/junction-hub-api/schemas/cancellation";
import { getSession } from "utils/auth";
import { getActionRequestJsonData } from "utils/common";
import { z } from "zod";

const cancelBookingsActionData = z.object({
  bookingIds: z.array(z.string().uuid()),
});
export type CancelBookingsActionData = z.infer<typeof cancelBookingsActionData>;

export const actions = {
  async cancelBookings(event): Promise<{ cancellation: CancellationRequest } | ActionFailure> {
    try {
      const data = await getActionRequestJsonData(event, cancelBookingsActionData);

      return {
        cancellation: await integrationInstances.junctionHubApi.cancellations.create({
          session: getSession(event),
          data,
        }),
      };
    } catch (err) {
      if (ensureJunctionError(err)) {
        return fail(500);
      }

      return fail(400);
    }
  },
};
