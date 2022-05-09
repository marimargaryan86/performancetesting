import { get, writable, type Readable, type Writable } from "svelte/store";

export function checkboxGroup(values: Writable<string[]>): {
  toggleAll: (ev: Event) => void;
  group: Writable<string[]>;
  allChecked: Readable<boolean>;
  multiSelect: (index: number) => void;
  unsubscriber: () => void;
} {
  const group = writable<string[]>([]);
  const allChecked = writable(false);
  let shiftDown = false;
  let lastSelectedIndex: number;

  const groupUnsub = group.subscribe(() => {
    allChecked.set(isAllChecked());
  });

  const valuesUnsub = values.subscribe((values) => {
    group.update((state) => state.filter((value) => values.indexOf(value) !== -1));
    allChecked.set(isAllChecked());
  });

  function isAllChecked(): boolean {
    const valuesState = get(values);
    const groupState = get(group);

    return valuesState.reduce((prev, curr) => prev && groupState.indexOf(curr) !== -1, true);
  }

  function toggleAll(ev: Event): void {
    group.set((ev.target as HTMLInputElement).checked ? get(values) : []);
  }

  function multiSelect(index: number): void {
    const groupState = get(group);
    const valuesState = get(values);

    if (isNaN(lastSelectedIndex)) {
      lastSelectedIndex = index;
    }

    if (!shiftDown) {
      lastSelectedIndex = index;

      return;
    }

    const mode = groupState.indexOf(valuesState[index]) === -1 ? "select" : "deselect";
    const start = Math.min(index, lastSelectedIndex);
    const end = Math.max(index, lastSelectedIndex) + 1;
    const nextGroup = valuesState.slice(start, end);

    if (mode === "select") {
      group.update((state) => Array.from(new Set([...state, ...nextGroup])));
    } else {
      group.update((state) => state.filter((placeId) => nextGroup.indexOf(placeId) === -1));
    }
  }

  function toggleShift(e: KeyboardEvent) {
    shiftDown = e.shiftKey || false;
  }

  if (typeof window !== "undefined") {
    window.addEventListener("focus", toggleShift);
    window.addEventListener("keydown", toggleShift);
    window.addEventListener("keyup", toggleShift);
  }

  function unsubscriber(): void {
    groupUnsub();
    valuesUnsub();

    window.removeEventListener("focus", toggleShift);
    window.removeEventListener("keydown", toggleShift);
    window.removeEventListener("keyup", toggleShift);
  }

  return {
    toggleAll,
    group,
    allChecked,
    multiSelect,
    unsubscriber,
  };
}
