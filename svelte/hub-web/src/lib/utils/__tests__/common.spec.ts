import { describe, expect, it, vi } from "vitest";
import { sleep, isUpperCase, getInitials, getHexColor, capitalize } from "../common";

describe("sleep function", () => {
  it("should resolve after specified time", async () => {
    vi.useFakeTimers();
    const start = Date.now();
    const sleepPromise = sleep(1000);
    vi.advanceTimersByTime(1000);
    await sleepPromise;
    const end = Date.now();
    expect(end - start).toBeGreaterThanOrEqual(1000);
    vi.useRealTimers();
  });
});

describe("isUpperCase function", () => {
  describe("with English characters", () => {
    it("should return true for all uppercase letters", () => {
      expect(isUpperCase("HELLO")).toBe(true);
    });

    it("should return false for mixed case letters", () => {
      expect(isUpperCase("Hello")).toBe(false);
      expect(isUpperCase("h3Ll0")).toBe(false);
    });

    it("should return false for all lowercase letters", () => {
      expect(isUpperCase("hello")).toBe(false);
    });

    it("should return false for strings containing only numbers", () => {
      expect(isUpperCase("0000")).toBe(false);
      expect(isUpperCase("1337")).toBe(false);
    });
  });

  describe("with German characters", () => {
    it("should return true for strings with German uppercase letters", () => {
      expect(isUpperCase("ÄPFEL")).toBe(true);
      expect(isUpperCase("ÖSTERREICH")).toBe(true);
    });

    it("should return false for strings with German lowercase letters", () => {
      expect(isUpperCase("äpfel")).toBe(false);
      expect(isUpperCase("Österreich")).toBe(false);
    });
  });

  describe("with Russian characters", () => {
    it("should return true for strings with Russian uppercase letters", () => {
      expect(isUpperCase("РОССИЯ")).toBe(true);
    });

    it("should return false for strings with Russian mixed case letters", () => {
      expect(isUpperCase("Россия")).toBe(false);
    });
  });

  describe("with languages without uppercase concept", () => {
    it("should return true for Arabic strings", () => {
      // Arabic doesn't have a disctinction between upper and lower case
      expect(isUpperCase("مرحبا")).toBe(true);
    });
  });

  describe("with Greek characters", () => {
    it("should return true for strings with Greek uppercase letters", () => {
      expect(isUpperCase("ΧΑΊΡΕΤΕ")).toBe(true);
    });

    it("should return false for strings with Greek mixed case letters", () => {
      expect(isUpperCase("Χαίρετε")).toBe(false);
    });
  });
});

describe("getInitials function", () => {
  it("should correctly get initials from a name", () => {
    expect(getInitials("John Doe")).toBe("JD");
    expect(getInitials("john doe")).toBe("JD");
    expect(getInitials("Jane")).toBe("J");
    expect(getInitials("McDonald")).toBe("MD");
    expect(getInitials("MacDonald")).toBe("MD");
    expect(getInitials("Mary MacDonald")).toBe("MMD");
  });

  it("should handle names with accents and special characters", () => {
    expect(getInitials("José Almeida")).toBe("JA");
    expect(getInitials("François Hollande")).toBe("FH");
    expect(getInitials("Jürgen Müller")).toBe("JM");
    expect(getInitials("İlkay Gündoğan")).toBe("İG");
    expect(getInitials("Björn Borg")).toBe("BB");
    expect(getInitials("Søren Kierkegaard")).toBe("SK");
    expect(getInitials("D'Angelo")).toBe("DA");
    expect(getInitials("Anne-Marie")).toBe("AM");
    expect(getInitials("Jean-Luc Picard")).toBe("JLP");
  });

  it("should handle names with non-Latin characters correctly", () => {
    expect(getInitials("Александр Сергеевич Пушкин")).toBe("АСП");
    expect(getInitials("李白")).toBe("李");
    expect(getInitials("김현우")).toBe("김");
    expect(getInitials("محمد الرفاعي")).toBe("ما");
  });
});

describe("getHexColor function", () => {
  it("should return a hex color based on a string", () => {
    const color = getHexColor("Hello");
    expect(color).toMatch(/^#[0-9a-f]{6}$/i);
  });
});

describe("capitalize function", () => {
  it("should capitalize the first letter of a string", () => {
    expect(capitalize("hello")).toBe("Hello");
    expect(capitalize("WORLD")).toBe("WORLD");
    expect(capitalize("javaScript")).toBe("JavaScript");
  });
});
