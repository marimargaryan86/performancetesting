import { sleep } from "./common";

/**
 * Wrap a function to make a polling function.
 *
 * @param func The function to wrap
 * @param check A checking function that determines whether the polling is `done`, `pending` or
 * a `retry` should be made
 * @param newArgs A function that checks if `func`'s arguments have changed. When true,
 * the previous execution will be cancelled and a new execution will start
 * @param sleepMs The time in milliseconds to sleep between polls
 * @param retries Number of times a retry should be made if the `check` function
 * returns a `retry` status
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function pollableCall<TFunc extends (...args: any[]) => any, TData>({
  func,
  check,
  newArgs = (prevArgs, nextArgs): boolean =>
    !prevArgs.reduce((prev, curr, idx) => prev && curr === nextArgs[idx], true),
  sleepMs = 1000,
  retries = 0,
}: {
  func: TFunc;
  check: (
    result: Awaited<ReturnType<TFunc>>,
  ) => { status: "done" | "retry"; data?: TData } | { status: "pending" };
  sleepMs?: number;
  newArgs?: (prevArgs: Parameters<TFunc>, nextArgs: Parameters<TFunc>) => boolean;
  retries?: number;
}): {
  poll: (...args: Parameters<TFunc>) => Promise<TData | undefined>;
  cancel: () => void;
} {
  let cancelled = false;
  let prevArgs: Parameters<TFunc>;

  function poll(...args: Parameters<TFunc>): Promise<TData | undefined> {
    prevArgs = args;

    let retryCount = 0;

    async function inner(): Promise<TData | undefined> {
      const result = check(await func(...args));

      if (cancelled || newArgs(prevArgs, args)) {
        return undefined;
      }

      if (result.status === "done") {
        return result.data;
      } else if (result.status === "retry") {
        if (retryCount >= retries) {
          return result.data;
        }

        retryCount++;
      }

      await sleep(sleepMs);

      return inner();
    }

    return inner();
  }

  return { poll, cancel: () => (cancelled = true) };
}
