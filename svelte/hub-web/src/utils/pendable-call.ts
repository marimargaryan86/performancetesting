import { writable, type Readable } from "svelte/store";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function pendableCall<TFunc extends (...args: any[]) => any>(
  func: TFunc,
): {
  pending: Readable<boolean>;
  func: (...args: Parameters<TFunc>) => Promise<Awaited<ReturnType<TFunc>>>;
} {
  const pending = writable(false);
  let task: ReturnType<TFunc> | undefined = undefined;

  return {
    pending,
    async func(...args: Parameters<TFunc>): Promise<Awaited<ReturnType<TFunc>>> {
      if (task !== undefined) {
        return task;
      }

      try {
        pending.set(true);
        task = func(...args);

        return (await task) as Promise<Awaited<ReturnType<TFunc>>>;
      } finally {
        pending.set(false);
        task = undefined;
      }
    },
  };
}
