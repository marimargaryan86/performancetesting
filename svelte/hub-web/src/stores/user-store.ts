import { writable } from "svelte/store";
import type { UserModel } from "models/user";

export default writable<UserModel>(undefined);
