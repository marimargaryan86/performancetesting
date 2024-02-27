import { database } from "$lib/data/database";

export const prerender = false;

/** @type {import('./$types').PageServerLoad} */
export function load(): { data: { title: string } } {
  const data = {
    title: "Landing",
    holidayPackages: database.holidayPackages,
    holidayCategories: database.holidayCategories,
    featuredPackages: database.featuredPackages,
    weatherHolidays: database.weatherHolidays,
  };

  return { data };
}
