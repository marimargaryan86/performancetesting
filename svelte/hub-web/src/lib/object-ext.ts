function keys<T extends object>(o: T): (keyof T)[] {
  return Object.keys(o) as (keyof T)[];
}

function entries<T extends object>(o: T): { [key in keyof T]: [key, T[key]] }[keyof T][] {
  return Object.entries(o) as { [key in keyof T]: [key, T[key]] }[keyof T][];
}

/* eslint-disable @typescript-eslint/no-explicit-any */
function fromEntries<
  TEntries extends [PropertyKey, any],
  // eslint-disable-next-line @typescript-eslint/no-shadow
>(entries: TEntries[]): { [entry in TEntries as entry[0]]: entry[1] } {
  return Object.fromEntries(entries) as { [entry in TEntries as entry[0]]: entry[1] };
}
/* eslint-enable @typescript-eslint/no-explicit-any */

export default {
  ...Object,
  keys,
  entries,
  fromEntries,
};
