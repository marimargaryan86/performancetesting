import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { Unsubscriber } from "svelte/store";
import userStore from "stores/user-store";
import type { UserModel } from "models/user";

const testUser1: UserModel = {
  id: "7229f0be-bafd-4920-ae69-e88968ae2831",
  email: "user1@example.com",
  name: "User One",
};

const testUser2: UserModel = {
  id: "8c98e6d7-aacc-4b5a-977b-68fed56deee8",
  email: "user2@example.com",
  name: "User Two",
};

describe("userStore", () => {
  let subscribed: UserModel | null | undefined;
  let unsubscribeCallback: Unsubscriber | (() => void) = vi.fn();

  beforeEach(() => {
    unsubscribeCallback = userStore.subscribe((value) => {
      subscribed = value;
    });
  });

  afterEach(() => {
    unsubscribeCallback();
    subscribed = undefined;
    unsubscribeCallback = vi.fn();
  });

  it("should initialize with `null`", () => {
    expect(subscribed).toBeUndefined();
  });

  it("should update when `setCurrentUser` is called", () => {
    userStore.set(testUser1);
    expect(subscribed).toEqual(testUser1);

    userStore.set(testUser2);
    expect(subscribed).toEqual(testUser2);
  });
});
