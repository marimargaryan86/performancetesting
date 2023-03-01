export function getRandomId(prefix = ""): string {
  return `${prefix}${Math.random().toString(36)}`;
}
