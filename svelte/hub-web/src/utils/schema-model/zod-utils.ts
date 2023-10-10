import { z } from "zod";

export type ZodNonNullable<T extends z.ZodTypeAny> = T extends z.ZodOptional<infer U>
  ? z.ZodOptional<ZodNonNullable<U>>
  : T extends z.ZodNullable<infer U>
  ? ZodNonNullable<U>
  : T;

export type ZodNonOptional<T extends z.ZodTypeAny> = T extends z.ZodOptional<infer U>
  ? ZodNonOptional<U>
  : T extends z.ZodNullable<infer U>
  ? z.ZodNullable<ZodNonOptional<U>>
  : T;

export type ZodNonNullish<T extends z.ZodTypeAny> = T extends z.ZodOptional<infer U>
  ? ZodNonNullish<U>
  : T extends z.ZodNullable<infer U>
  ? ZodNonNullish<U>
  : T;

export type ZodIsOptional<T extends z.ZodTypeAny> = undefined extends z.infer<T> ? true : false;
export type ZodIsNullable<T extends z.ZodTypeAny> = null extends z.infer<T> ? true : false;

export function zodNonNullish<T extends z.ZodTypeAny>(value: T): ZodNonNullish<T> {
  if (value instanceof z.ZodOptional) {
    return zodNonNullish(value.unwrap());
  }

  if (value instanceof z.ZodNullable) {
    return zodNonNullish(value.unwrap());
  }

  return value as ZodNonNullish<T>;
}

export function zodNonOptional<T extends z.ZodTypeAny>(value: T): ZodNonOptional<T> {
  if (value instanceof z.ZodOptional) {
    return zodNonOptional(value.unwrap());
  }

  if (value instanceof z.ZodNullable) {
    return zodNonOptional(value.unwrap()).nullable();
  }

  return value as ZodNonOptional<T>;
}
