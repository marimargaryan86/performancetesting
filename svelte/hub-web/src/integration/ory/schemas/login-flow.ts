import type { AuthenticatorAssurenceLevel, CredentialsType } from "./common";
import { uiContainerParser, type UiContainer, type UiContainerSchema } from "./ui-container";

export type OAuth2ClientSchema = {
  access_token_strategy?: string;
  allowed_cors_origins?: string[];
  audience?: string[];
  authorization_code_grant_access_token_lifespan?: string | null;
  authorization_code_grant_id_token_lifespan?: string | null;
  authorization_code_grant_refresh_token_lifespan?: string | null;
  backchannel_logout_session_required?: boolean;
  backchannel_logout_uri?: string;
  client_credentials_grant_access_token_lifespan?: string | null;
  client_id?: string;
  client_name?: string;
  client_secret?: string;
  client_secret_expires_at?: number;
  client_uri?: string;
  contacts?: string[];
  created_at?: string;
  frontchannel_logout_session_required?: boolean;
  frontchannel_logout_uri?: string;
  grant_types?: string[];
  implicit_grant_access_token_lifespan?: string | null;
  implicit_grant_id_token_lifespan?: string | null;
  jwks?: unknown;
  jwks_uri?: string;
  jwt_bearer_grant_access_token_lifespan?: string | null;
  logo_uri?: string;
  metadata?: object;
  owner?: string;
  policy_uri?: string;
  post_logout_redirect_uris?: string[];
  redirect_uris?: string[];
  refresh_token_grant_access_token_lifespan?: string | null;
  refresh_token_grant_id_token_lifespan?: string | null;
  refresh_token_grant_refresh_token_lifespan?: string | null;
  registration_access_token?: string;
  registration_client_uri?: string;
  request_object_signing_alg?: string;
  request_uris?: string[];
  response_types?: string[];
  scope?: string;
  sector_identifier_uri?: string;
  skip_consent?: boolean;
  subject_type?: string;
  token_endpoint_auth_method?: string;
  token_endpoint_auth_signing_alg?: string;
  tos_uri?: string;
  updated_at?: string;
  userinfo_signed_response_alg?: string;
};

export type OpenIDConnectRequestSchema = {
  acr_values?: string[];
  display?: string;
  id_token_hint_claims?: Record<string, unknown>;
  login_hint?: string;
  ui_locales?: string[];
};

export type OAuth2LoginRequestSchema = {
  challenge: string;
  client: OAuth2ClientSchema;
  oidc_context?: OpenIDConnectRequestSchema;
  request_url: string;
  requested_access_token_audience: string[];
  requested_scope: string[];
  session_id?: string;
  skip: boolean;
  subject: string;
};

export type LoginFlowState = "choose_method" | "sent_email" | "passed_challenge";

export type LoginFlow = {
  active?: CredentialsType;
  createdAt?: Date;
  expiresAt: Date;
  id: string;
  issuedAt: Date;
  organizationId?: string;
  refresh: boolean;
  requestUrl: string;
  requestedAal?: AuthenticatorAssurenceLevel;
  returnTo?: string;
  sessionTokenExchangeCode?: string;
  state: LoginFlowState;
  type: "api" | "browser";
  ui: UiContainer;
  updatedAt?: Date;
};

export type LoginFlowSchema = {
  active?: CredentialsType;
  created_at?: string;
  expires_at: string;
  id: string;
  issued_at: string;
  oauth2_login_challend?: string;
  oauth2_login_request?: OAuth2LoginRequestSchema;
  organization_id?: string | null;
  refresh?: boolean;
  request_url: string;
  requested_aal?: AuthenticatorAssurenceLevel;
  return_to?: string;
  session_token_exchange_code?: string;
  state: LoginFlowState;
  type: "api" | "browser";
  ui: UiContainerSchema;
  updated_at?: string;
};

export const loginFlowParser = {
  toModel: (data: LoginFlowSchema): LoginFlow => ({
    active: data.active,
    createdAt: data.created_at ? new Date(data.created_at) : undefined,
    expiresAt: new Date(data.expires_at),
    id: data.id,
    issuedAt: new Date(data.issued_at),
    organizationId: data.organization_id ?? undefined,
    refresh: Boolean(data.refresh),
    requestUrl: data.request_url,
    requestedAal: data.requested_aal,
    returnTo: data.return_to,
    sessionTokenExchangeCode: data.session_token_exchange_code,
    state: data.state,
    type: data.type,
    ui: uiContainerParser.toModel(data.ui),
    updatedAt: data.updated_at ? new Date(data.updated_at) : undefined,
  }),
};
