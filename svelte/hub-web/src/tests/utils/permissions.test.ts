import { describe, expect, it } from "vitest";
import { permitted } from "../../utils/permissions";
import type { UserModel } from "../../models/user";

const adminUser: UserModel = {
  id: "0001",
  email: "admin@example.com",
  name: "admin",
  permissions: {
    "*": {},
  },
};

const snowfallUser: UserModel = {
  id: "0002",
  email: "user@example.com",
  name: "snowfall-user",
  permissions: {
    "journey.view": {},
    "order.view": {},
    "booking.view": {},
    "cancel.*": {},
    "refund.*": {},
    "transaction.*": {},
  },
};

const resellerUser: UserModel = {
  id: "0003",
  email: "reseller.user@example.com",
  name: "reseller-user",
  permissions: {
    "journey.*": {
      "attributes.resellerId": ["~", ["0042"]],
    },
    "order.*": {
      "attributes.resellerId": ["~", ["0042"]],
    },
    "booking.*": {
      "attributes.resellerId": ["~", ["0042"]],
    },
    "cancel.add": {
      "attributes.resellerId": ["~", ["0042"]],
    },
    "cancel.view": {
      "attributes.resellerId": ["~", ["0042"]],
    },
    "refund.view": {
      "attributes.resellerId": ["~", ["0042"]],
    },
  },
};

const resellerAdmin: UserModel = {
  id: "0004",
  email: "reseller.admin@example.com",
  name: "reseller-admin",
  permissions: {
    ...resellerUser.permissions,
    "user.*": {
      "attributes.resellerId": ["~", ["0042"]],
    },
  },
};

describe("permitted", () => {
  it("returns true for specific permission", () => {
    expect(permitted(snowfallUser, "booking", "view")).toBe(true);
  });

  it("returns true for wildcard module permission", () => {
    expect(permitted(resellerAdmin, "order", "view")).toBe(true);
  });

  it("returns true for global permission", () => {
    expect(permitted(adminUser, "transaction", "view")).toBe(true);
  });

  it("returns false when user has no permission", () => {
    expect(permitted(resellerUser, "user", "view")).toBe(false);
  });

  it("handles undefined action parameter", () => {
    expect(permitted(resellerAdmin, "user")).toBe(true);
    expect(permitted(resellerUser, "user")).toBe(false);
  });
});
