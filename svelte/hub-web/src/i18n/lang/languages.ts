export default [
  { locale: "en-GB" as const, flag: "🇬🇧", name: "EN" },
  { locale: "sv" as const, flag: "🇸🇪", name: "SV" },
  { locale: "es-ES" as const, flag: "🇪🇸", name: "ES" },
] satisfies { locale: string; flag: string; name: string }[];
