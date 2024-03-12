import { createRPCBase } from "$lib/rpc-base";
import * as devalue from "devalue";
import { z } from "zod";
import { JunctionError, ensureJunctionError } from "~/integration/common/junction-error";

const CLIENT_REDUCERS = {
  /** Add TZ offset on client side requests to make dates TZ agnostic */
  Date: (value: unknown): string | undefined => {
    if (value instanceof Date) {
      const date = new Date(value);
      const tzOffset = date.getTimezoneOffset();
      date.setMinutes(date.getMinutes() - tzOffset);

      return date.toISOString();
    }

    return undefined;
  },
};
const CLIENT_REVIVERS = {
  Date: (value: unknown): Date | undefined => {
    if (typeof value === "string") {
      return new Date(value);
    }

    return undefined;
  },
} satisfies Record<keyof typeof CLIENT_REDUCERS, (value: unknown) => unknown>;

export default createRPCBase({
  responseParser: devalue,
  requestParser: {
    stringify: (data) => devalue.stringify(data, CLIENT_REDUCERS),
    parse: (data) => devalue.parse(data, CLIENT_REVIVERS),
  },
  errorParser: {
    serialize(data) {
      if (data instanceof z.ZodError) {
        return {
          type: "ZodError",
          args: [data.issues],
        } as const;
      }

      if (data instanceof JunctionError) {
        return {
          type: "JunctionError",
          args: [
            {
              traceId: data.traceId,
              status: data.status,
              statusText: "",
              json: data.json,
              requestId: data.requestId,
            },
          ],
        } as const;
      }

      return {
        type: "Error",
        args: [data.message],
      } as const;
    },
    deserialize(data) {
      if (data.type === "ZodError") {
        return new z.ZodError(...data.args);
      }

      if (data.type === "JunctionError") {
        return new JunctionError(...data.args);
      }

      return new Error(...data.args);
    },
  },
  onErrorResponse(event, error) {
    if (ensureJunctionError(error)) {
      event.setHeaders({
        "x-request-id": error.requestId ?? "unknown",
        "x-trace-id": error.traceId ?? "unknown",
      });
    }
  },
});
