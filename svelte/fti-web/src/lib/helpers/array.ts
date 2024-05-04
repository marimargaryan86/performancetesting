/**
 * Checks if the given value is defined (not undefined).
 *
 * This is a type guard function that helps TypeScript narrow down the type
 * by filtering out undefined values from a type that could be undefined or another type.
 *
 * @param {T | undefined} value - The value to check for undefined.
 * @returns {boolean} True if the value is not undefined, otherwise false.
 * @template T - The type of the value being checked.
 */
export function ensureDefined<T>(value: T | undefined): value is T {
  return value !== undefined;
}
