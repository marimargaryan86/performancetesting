export function getRandomId(prefix?: string): string {
  return `${prefix ? `${prefix}-` : "a-"}${Math.random().toString(32)}`;
}
