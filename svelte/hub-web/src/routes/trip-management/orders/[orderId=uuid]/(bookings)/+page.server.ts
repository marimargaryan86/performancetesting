import { type ActionFailure, fail } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import { ensureJunctionError } from "integration/common/junction-error";
import type { CancellationRequestModel } from "integration/junction-mobile-api/schemas/cancellation-request";
import { getSession } from "utils/auth";
import { getActionRequestJsonData } from "utils/common";
import { z } from "zod";

const cancelBookingsActionData = z.object({
  bookingIds: z.array(z.string().uuid()),
});
export type CancelBookingsActionData = z.infer<typeof cancelBookingsActionData>;

export const actions = {
  async cancelBookings(event): Promise<{ cancellation: CancellationRequestModel } | ActionFailure> {
    try {
      const data = await getActionRequestJsonData(event, cancelBookingsActionData);

      return {
        cancellation:
          await integrationInstances.junctionMobileApi.cancellations.createCancellationRequest({
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
