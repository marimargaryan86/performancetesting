export function match(param: string): boolean {
  return Boolean(param.match(/^add|[A-f0-9]{8}-[A-f0-9]{4}-[A-f0-9]{4}-[A-f0-9]{4}-[A-f0-9]{12}$/));
}
