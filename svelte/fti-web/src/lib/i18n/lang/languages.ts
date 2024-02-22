export default [
  { locale: "en-GB" as const, flag: "🇬🇧", name: "EN" },
  { locale: "de" as const, flag: "🇩🇪", name: "DE" },
] satisfies { locale: string; flag: string; name: string }[];
