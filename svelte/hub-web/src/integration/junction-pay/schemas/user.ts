export interface UserJwtSchema {
  custom: Record<string, unknown>;
  exp: number;
  jti: string;
  user_info: {
    id: string;
    email: string;
    metadata: Record<string, unknown>;
  };
  verstion: string;
}
