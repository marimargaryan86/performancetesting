import { ensureDefined } from "$lib/utils/array";
import { EMPTY_OBJECT } from "./constants";

export function conditionalQuotes(str: string): string {
  if (str.match(/^[A-Za-z_$][A-Za-z0-9_$]*$/)) {
    return str;
  }

  return `"${str}"`;
}

export function toStringObject(
  properties: (`${string}: ${string}` | undefined)[],
  indent: number,
): string {
  const filtered = properties.filter(ensureDefined);

  if (!filtered.length) {
    return EMPTY_OBJECT;
  }

  const padding = "".padStart(indent);

  return `{\n  ${filtered.map((item) => `${padding}${item}`).join(";\n  ")};\n${padding}}`;
}

export function maybeOptionalProp(
  name: string,
  required: boolean,
  value: string,
): `${string}: ${string}` {
  return `${name}${required ? "" : "?"}: ${value}`;
}
