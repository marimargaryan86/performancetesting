export type User = {
  id: string;
};

export type UserSchema = {
  id: string;
  type: "users";
  attributes: unknown;
};

export const userParser = {
  toModel: (data: UserSchema): User => ({
    id: data.id,
  }),
};
