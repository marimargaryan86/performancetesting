export function getPageTitle(...part: string[]): string {
  return part.reverse().join(" · ");
}
