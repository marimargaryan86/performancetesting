export function sleep(timeMs: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, timeMs));
}

export function isUpperCase(value: string): boolean {
  // Early return if the string is empty or contains only non-alphabetic characters
  if (value.length === 0 || !/\p{L}/u.test(value)) {
    return false;
  }

  // Check if all alphabetic characters are uppercase
  for (let i = 0; i < value.length; i++) {
    const char = value[i];
    // If the character is alphabetic and not uppercase, return false
    if (char !== undefined && /\p{L}/u.test(char) && char !== char.toLocaleUpperCase()) {
      return false;
    }
  }

  // If the loop completes without returning false, all alphabetic characters are uppercase
  return true;
}

export function getInitials(name: string): string {
  return (
    name
      // Split the name by whitespace characters
      .split(/\s+/)
      .map((part) => {
        // Find all uppercase letters in the part
        const uppercaseLetters = part.match(/[A-Z]/g) || [];
        // If there are more than one uppercase letters, use the first two, otherwise use the first letter
        if (uppercaseLetters.length > 1 && uppercaseLetters[0]) {
          return uppercaseLetters[0] + uppercaseLetters[1];
        }
        return part[0];
      })
      .join("")
      .toUpperCase()
  );
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

export function capitalize([first, ...rest]: string): string {
  return `${first?.toUpperCase()}${rest.join("")}`;
}

export function startsWith(target: string, ...prefixes: string[]): boolean {
  return prefixes.some(target.startsWith);
}
