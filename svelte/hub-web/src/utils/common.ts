import { applyAction, deserialize } from "$app/forms";
import type { ActionResult } from "@sveltejs/kit";

export function sleep(timeMs: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, timeMs));
}

export function isUpperCase(value: string): boolean {
  return value.toUpperCase() === value;
}

export function getInitials(name: string): string {
  const alpha = name.replace(/[^A-z]/g, "");
  const parts = alpha.split(" ").filter((part) => part.trim().length);

  if (parts.length > 1) {
    return `${parts[0]?.[0]?.toUpperCase()}${parts[1]?.[0]?.toUpperCase()}`;
  }

  let result = parts[0]?.[0] as string;

  for (const char of parts[0]?.substring(1) ?? "") {
    if (isUpperCase(char)) {
      result += char;
    }

    if (result.length === 2) {
      break;
    }
  }

  return result.toUpperCase();
}

export function getHexColor(value: string): string {
  const sum = Array.from(value).reduce((prev, curr) => prev + curr.charCodeAt(0) * 100000, 0);
  const hex = sum.toString(16);
  const padding = Math.max(6 - hex.length, 0);

  if (padding > 0) {
    return `#${[...Array(padding)].map(() => "0")}${hex}`;
  }

  return `#${hex.substring(0, 6)}`;
}

export function capitalize(value: string): string {
  return `${value[0]?.toUpperCase()}${value.substring(1)}`;
}

export type FlattenedObject_<
  T extends Record<string, unknown>,
  TKey = keyof T,
> = TKey extends string
  ? T[TKey] extends Record<string, unknown>
    ? `${TKey}.${FlattenedObject_<Required<T[TKey]>>}`
    : TKey
  : never;

export type FlattenedObject<T extends Record<string, unknown>> = FlattenedObject_<Required<T>>;

export type RecursivePartial<T> = {
  [P in keyof T]?: T[P] extends (infer U)[]
    ? RecursivePartial<U>[]
    : T[P] extends object
    ? RecursivePartial<T[P]>
    : T[P];
};

export type PartiallyPartial<TObject extends object, TRequired extends keyof TObject> = {
  [key in TRequired]: TObject[key];
} & { [key in Exclude<keyof TObject, TRequired>]?: TObject[key] };

function getActionRequestData(data?: Record<string, unknown>): FormData | undefined {
  const formData = new FormData();

  if (!data) {
    return formData;
  }

  Object.entries(data).forEach(([key, val]) => {
    if (val !== undefined) {
      formData.set(key, String(val));
    }
  });

  return formData;
}

export async function callAction<
  TResult extends Record<string, unknown> = Record<string, unknown>,
  TFailure extends Record<string, unknown> = Record<string, unknown>,
>({
  action,
  data,
  apply = true,
}: {
  action: string;
  data?: Record<string, unknown>;
  apply?: boolean;
}): Promise<ActionResult<TResult, TFailure>> {
  const body = getActionRequestData(data);
  const resp = await fetch(action, { method: "POST", body });
  const result = deserialize<TResult, TFailure>(await resp.text());

  if (apply) {
    await applyAction(result);
  }

  return result;
}
