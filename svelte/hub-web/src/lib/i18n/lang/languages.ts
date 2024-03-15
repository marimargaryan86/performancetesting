export default [
  { locale: "en-GB" as const, flag: "🇬🇧", name: "EN" },
  { locale: "es-ES" as const, flag: "🇪🇸", name: "ES" },
] satisfies { locale: string; flag: string; name: string }[];
