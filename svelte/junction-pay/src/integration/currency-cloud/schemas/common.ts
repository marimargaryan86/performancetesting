export const orderDirections = ["asc", "desc"] as const;

export type OrderDirection = typeof orderDirections[number];
