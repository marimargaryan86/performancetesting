import type { User } from "integration/ory/schemas";
import { writable } from "svelte/store";

export default writable<User>(undefined);
