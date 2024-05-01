function pluralise(count: number, singular: string, plural: string): string {
  return count === 1 ? singular : plural;
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

export {
  pluralise,
  setContainerScroll,
  setDropdown,
  getMonthNames,
  renderStars,
  formatDate,
  calculateThisWeekDates,
};
