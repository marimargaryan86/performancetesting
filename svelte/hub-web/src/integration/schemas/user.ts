export interface UserJwtSchema {
  user_info: {
    email: string;
    password: string;
    id: string;
  };
  exp: number;
}
