import { uiContainerParser, type UiContainer, type UiContainerSchema } from "./ui-container";

type RecoveryFlowState = "choose_method" | "sent_email" | "passed_challenge";

export type RecoveryFlow = {
  active?: string;
  expiresAt: Date;
  id: string;
  issuedAt: Date;
  requestUrl: string;
  returnTo?: string;
  state: RecoveryFlowState;
  type: "api" | "browser";
  ui: UiContainer;
};

export type RecoveryFlowSchema = {
  active?: string;
  expires_at: string;
  id: string;
  issued_at: string;
  request_url: string;
  return_to?: string;
  state: RecoveryFlowState;
  type: "api" | "browser";
  ui: UiContainerSchema;
};

export const recoveryFlowParser = {
  toModel: (data: RecoveryFlowSchema): RecoveryFlow => ({
    active: data.active,
    expiresAt: new Date(data.expires_at),
    id: data.id,
    issuedAt: new Date(data.issued_at),
    requestUrl: data.request_url,
    returnTo: data.return_to,
    state: data.state,
    type: data.type,
    ui: uiContainerParser.toModel(data.ui),
  }),
};
