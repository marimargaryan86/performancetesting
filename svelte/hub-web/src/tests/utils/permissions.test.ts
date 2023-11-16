import { describe, expect, it } from "vitest";
import { permitted } from "../../utils/permissions";
import type { User } from "integration/ory/schemas";

const adminUser: User = {
  id: "0001",
  email: "admin@example.com",
  name: "admin",
  role: "snowfall-admin",
};

const snowfallUser: User = {
  id: "0002",
  email: "user@example.com",
  name: "snowfall-user",
  role: "snowfall-user",
};

const resellerUser: User = {
  id: "0003",
  email: "reseller.user@example.com",
  name: "reseller-user",
  role: "reseller-user",
};

const resellerAdmin: User = {
  id: "0004",
  email: "reseller.admin@example.com",
  name: "reseller-admin",
  role: "reseller-admin",
};

describe("permitted", () => {
  it("returns true for specific permission", () => {
    expect(permitted(snowfallUser, "booking.view")).toBe(true);
  });

  it("returns true for wildcard module permission", () => {
    expect(permitted(resellerAdmin, "order.view")).toBe(true);
  });

  it("returns true for global permission", () => {
    expect(permitted(adminUser, "transaction.view")).toBe(true);
  });

  it("returns false when user has no permission", () => {
    expect(permitted(resellerUser, "user.view")).toBe(false);
  });

  it("handles undefined action parameter", () => {
    expect(permitted(resellerAdmin, "user.add", "user.view")).toBe(true);
    expect(permitted(resellerUser, "user.add", "user.view")).toBe(false);
  });
});
