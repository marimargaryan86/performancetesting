export function isUpperCase(value: string): boolean {
  return value.toUpperCase() === value;
}

export function getInitials(name: string): string {
  const parts = name.split(" ").filter((part) => part.trim().length);

  if (parts.length > 1) {
    return `${parts[0]?.[0]?.toUpperCase()}${parts[1]?.[0]?.toUpperCase()}`;
  }

  let result = parts[0]?.[0] as string;

  for (const char of parts[0]?.substring(1) ?? "") {
    if (isUpperCase(char)) {
      result += char;
    }

    if (result.length === 2) {
      break;
    }
  }

  return result.toUpperCase();
}

export function getHexColor(value: string): string {
  const sum = Array.from(value).reduce((prev, curr) => prev + curr.charCodeAt(0) * 100000, 0);
  const hex = sum.toString(16);
  const padding = Math.max(6 - hex.length, 0);

  if (padding > 0) {
    return `#${[...Array(padding)].map(() => "0")}${hex}`;
  }

  return `#${hex.substring(0, 6)}`;
}
