function sleep(timeMs: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, timeMs));
}

function getPixelValue(value: string): number {
  return parseInt(value.replace("px", ""), 10);
}

function scrollIntoView(child?: Element) {
  if (!child) {
    return;
  }

  const parent = child.parentElement;
  const parentStyle = window.getComputedStyle(parent);
  const parentTopPadding =
    getPixelValue(parentStyle.paddingTop) + getPixelValue(parentStyle.borderTopWidth);
  const parentBottomPadding =
    getPixelValue(parentStyle.paddingBottom) + getPixelValue(parentStyle.borderBottomWidth);
  const parentInnerHeight =
    parent.getBoundingClientRect().height - (parentTopPadding + parentBottomPadding);
  const offsetTop =
    child.getBoundingClientRect().top - (parent.getBoundingClientRect().top + parentTopPadding);
  const childHeight = child.getBoundingClientRect().height;

  if (offsetTop < 0) {
    child.scrollIntoView(true);
  } else if (offsetTop + childHeight > parentInnerHeight) {
    child.scrollIntoView(false);
  }
}

const storage = {
  get<T = unknown>(key: string, parser?: (data: Record<string, unknown>) => T): T | undefined {
    try {
      sessionStorage;
    } catch {
      return undefined;
    }

    const raw = sessionStorage.getItem(key);

    if (!raw) {
      return undefined;
    }

    const data = JSON.parse(raw);

    if (!parser) {
      return data;
    }

    return parser(data);
  },
  set<T = unknown>(key: string, data: T, parser?: (data: T) => Record<string, unknown>): void {
    try {
      sessionStorage;
    } catch {
      return;
    }

    let nextData: T | Record<string, unknown> = data;

    if (parser) {
      nextData = parser(data);
    }

    sessionStorage.setItem(key, JSON.stringify(nextData));
  },
  remove(key: string): void {
    try {
      sessionStorage;
    } catch {
      return;
    }

    sessionStorage.removeItem(key);
  },
};

const fullDateTime: Intl.DateTimeFormatOptions = {
  year: "numeric",
  month: "numeric",
  day: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
};

export default {
  sleep,
  getPixelValue,
  scrollIntoView,
  storage,
  fullDateTime,
};
