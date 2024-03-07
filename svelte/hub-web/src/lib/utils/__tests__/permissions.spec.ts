import { describe, expect, it } from "vitest";
import type { User } from "~/integration/ory/schemas";
import { getPermission, permitted } from "../permissions";

describe("permissions.ts", () => {
  const mockUser: User = {
    id: "123",
    role: "reseller-user",
    email: "test.testerson@snowfalltravel.com",
  };

  describe("getPermission", () => {
    it("returns the permission number for the given actions", () => {
      const result = getPermission("journey.view", "order.view");
      expect(result).toBe(10);
    });
  });

  describe("permitted", () => {
    it("returns true if the user is permitted to perform the actions", () => {
      const result = permitted(mockUser, "journey.view", "order.view");
      expect(result).toBe(true);
    });

    it("returns false if the user is not permitted to perform the actions", () => {
      const result = permitted(mockUser, "users.edit");
      expect(result).toBe(false);
    });
  });
});
