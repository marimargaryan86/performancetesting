import type { AuthenticatorAssurenceLevel, CredentialsType } from "./common";

export type UserRole = "reseller-user" | "reseller-admin" | "snowfall-user" | "snowfall-admin";

export type RecoveryIdentityAddressSchema = {
  created_at?: string;
  id: string;
  updated_at?: string;
  value: string;
  via: string;
};

export type VerifiableIdentityAddressSchema = {
  created_at?: string;
  id?: string;
  status: string;
  updated_at?: string;
  value: string;
  verified: boolean;
  verified_at?: string;
  via: string;
};

export type IdentityCredentialsSchema = {
  config?: object;
  created_at?: string;
  identifiers?: string[];
  type?: CredentialsType;
  updated_at?: string;
  version?: number;
};

export type SessionDeviceSchema = {
  id: string;
  ip_address?: string;
  location?: string;
  user_agent?: string;
};

export type User = {
  id: string;
  role: UserRole;
  email: string;
};

export type OryKratosIdentitySchema = {
  created_at?: string;
  credentials?: Record<string, IdentityCredentialsSchema>;
  id: string;
  metadata_admin?: object | null;
  metadata_public: { role: UserRole };
  organization_id?: string | null;
  recovery_addresses?: RecoveryIdentityAddressSchema[];
  schema_id: string;
  schema_url: string;
  state?: "active" | "inactive";
  state_changed_at?: string;
  traits: { email: string };
  updated_at?: string;
  verifiable_addresses: VerifiableIdentityAddressSchema[];
};

export const oryKratosIdentityParser = {
  toModel: (data: OryKratosIdentitySchema): User => ({
    id: data.id,
    role: data.metadata_public.role,
    email: data.traits.email,
  }),
};

export type AuthenticationMethod =
  | "link_recovery"
  | "code_recovery"
  | "password"
  | "code"
  | "totp"
  | "oidc"
  | "webauthn"
  | "lookup_secret"
  | "v0.6_legacy_session";

export type AuthenticationSchema = {
  session: {
    active?: boolean;
    authenticated_at?: string;
    authentication_methods?: {
      aal?: AuthenticatorAssurenceLevel;
      compelted_at?: string;
      method?: AuthenticationMethod;
      organization?: string;
      provider?: string;
    }[];
    authenticator_assurance_level?: AuthenticatorAssurenceLevel;
    devices: SessionDeviceSchema[];
    expires_at: string;
    id: string;
    identity: OryKratosIdentitySchema;
    issued_at?: string;
    tokenized?: string;
  };
  session_token?: string;
};

export type Session = {
  id: string;
  token: string;
};

export type SessionMeta = {
  user: User;
  expiresAt: Date;
};
