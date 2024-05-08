function pluralise(count: number, singular: string, plural: string): string {
  return count === 1 ? singular : plural;
}

/**
 * Converts a given string to title case, where the first letter of each word
 * is capitalized and the rest are in lowercase.
 *
 * @param str - The string to convert to title case.
 * @returns The title-cased version of the input string.
 */
function toTitleCase(str: string): string {
  return str.toLowerCase().replace(/(?:^|\s|["'([{])+\S/g, (match) => match.toUpperCase());
}

const setContainerScroll = ({
  detail,
  className,
  amount,
}: {
  detail: boolean;
  className: string;
  amount: number;
}): void => {
  const container = document.querySelector(className);

  const delta = detail ? amount : -amount;
  if (container) {
    const currentScroll = container.scrollLeft;
    const newScroll = currentScroll + delta;
    container.scrollTo({ left: newScroll, behavior: "smooth" });
  }
};

const setDropdown = (value: string): string => {
  // if (dropdown === value) {
  //   return "";
  // }
  return value;
};

function getMonthNames(locale: string): string[] {
  return Array.from({ length: 12 }).reduce((acc: string[], _, index) => {
    // Year 0 is used as a workaround for getting month names
    const date = new Date(0, index);
    const monthName = new Intl.DateTimeFormat(locale, { month: "long" }).format(date);
    acc.push(monthName);
    return acc;
  }, []);
}

const renderStars = (stars: number): string[] => {
  return Array.from({ length: stars }, () => "⭐");
};

function formatDate(date: Date): string {
  return date.toISOString().split("T")[0];
}

function calculateThisWeekDates() {
  const today = new Date();
  const nextSunday = new Date(today.setDate(today.getDate() + (7 - today.getDay())));
  const followingSunday = new Date(nextSunday.getTime() + 7 * 24 * 60 * 60 * 1000);

  return {
    arriveAt: formatDate(nextSunday),
    returnAt: formatDate(followingSunday),
  };
}

/**
 * Generates a URL-friendly slug from a given string. The function performs several transformations:
 * 1. Converts all characters to lowercase to ensure uniformity.
 * 2. Replaces spaces with hyphens to create web-friendly word separators.
 * 3. Removes all non-alphanumeric characters except hyphens, filtering out unwanted punctuation and symbols.
 * 4. Collapses any sequences of multiple hyphens into a single hyphen to avoid URL parsing issues and improve aesthetics.
 *
 * @param {string} name - The input string from which to generate the slug.
 * @returns {string} The URL-friendly slug.
 */
function createSlug(name: string): string {
  return name
    .toLowerCase()
    .replace(/ /g, "-")
    .replace(/[^\w-]+/g, "")
    .replace(/-+/g, "-");
}

export {
  pluralise,
  setContainerScroll,
  setDropdown,
  getMonthNames,
  renderStars,
  formatDate,
  calculateThisWeekDates,
  toTitleCase,
  createSlug,
};
