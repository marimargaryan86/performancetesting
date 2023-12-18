export default [
  { locale: "en-GB" as const, flag: "🇬🇧", name: "EN" },
  { locale: "sv-SE" as const, flag: "🇸🇪", name: "SV" },
] satisfies { locale: string; flag: string; name: string }[];
