import type { User } from "integration/ory/schemas/authentication";
import { writable } from "svelte/store";

export default writable<User>(undefined);
