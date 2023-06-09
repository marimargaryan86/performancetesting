import type { z } from "zod";

export type FormattedError<TSchema> = TSchema extends Record<string, unknown>
  ? { [key in keyof TSchema]?: FormattedError<TSchema[key]> }
  : string;

function formatErrorAux<TSchema>(error: z.ZodFormattedError<TSchema>): FormattedError<TSchema> {
  const keys = Object.keys(error);

  if (keys.length === 1) {
    return error._errors.join(", ") as FormattedError<TSchema>;
  }

  const errorObj = error as Record<string, z.ZodFormattedError<unknown>>;

  return Object.fromEntries(
    Object.entries(errorObj)
      .map(([key, val]) => [key, formatErrorAux(val)])
      .filter(([key, val]) => key !== "_errors" && Boolean(val)),
  );
}

export function formatError<TSchema>(error: z.ZodError<TSchema>): FormattedError<TSchema> {
  const formatted = error.format();

  return formatErrorAux(formatted);
}
