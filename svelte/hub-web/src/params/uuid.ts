import { z } from "zod";

const uuid = z.string().uuid();

export function match(param: string): boolean {
  try {
    uuid.parse(param);

    return true;
  } catch {
    return false;
  }
}
