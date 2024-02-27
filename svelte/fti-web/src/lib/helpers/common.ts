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
  // const months: string[] = [];
  return Array.from({ length: 12 }).reduce((acc: string[], _, index) => {
    // Year 0 is used as a workaround for getting month names
    const date = new Date(0, index);
    const monthName = new Intl.DateTimeFormat(locale, { month: "long" }).format(date);
    acc.push(monthName);
    return acc;
  }, []);
}

export { pluralise, setContainerScroll, setDropdown, getMonthNames };
