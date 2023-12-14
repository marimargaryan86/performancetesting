export default [
  { locale: "en-GB" as const, name: "English (UK)" },
  { locale: "sv-SE" as const, name: "Svenska" },
] satisfies { locale: string; name: string }[];
