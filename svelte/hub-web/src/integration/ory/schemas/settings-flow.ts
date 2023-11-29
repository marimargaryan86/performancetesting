import { oryKratosIdentityParser, type OryKratosIdentitySchema, type User } from "./authentication";
import { uiContainerParser, type UiContainer, type UiContainerSchema } from "./ui-container";

export type SettingsFlow = {
  active?: string;
  continueWith: (
    | {
        action: "session";
        token: string;
      }
    | {
        action: "verification";
        flow: {
          id: string;
          verifiableAddress: string;
          url?: string;
        };
      }
  )[];
  expiresAt: Date;
  id: string;
  user: User;
  issuedAt: Date;
  requestUrl: string;
  returnTo?: string;
  state: "show_form" | "success";
  ui: UiContainer;
};

export type SettingsFlowSchema = {
  active?: string;
  continue_with?: (
    | {
        action: "set_ory_session_token";
        ory_session_token: string;
      }
    | {
        action: "show_verification_ui";
        flow: {
          id: string;
          url?: string;
          verifiable_address: string;
        };
      }
  )[];
  expires_at: string;
  id: string;
  identity: OryKratosIdentitySchema;
  issued_at: string;
  request_url: string;
  return_to?: string;
  state: "show_form" | "success";
  type: "api" | "browser";
  ui: UiContainerSchema;
};

export const settingsFlowParser = {
  toModel: (data: SettingsFlowSchema): SettingsFlow => ({
    active: data.active,
    continueWith:
      data.continue_with?.map<SettingsFlow["continueWith"][number]>((item) => {
        return item.action === "set_ory_session_token"
          ? { action: "session", token: item.ory_session_token }
          : {
              action: "verification",
              flow: {
                id: item.flow.id,
                verifiableAddress: item.flow.verifiable_address,
                url: item.flow.url,
              },
            };
      }) ?? [],
    expiresAt: new Date(data.expires_at),
    id: data.id,
    issuedAt: new Date(data.issued_at),
    requestUrl: data.request_url,
    state: data.state,
    ui: uiContainerParser.toModel(data.ui),
    user: oryKratosIdentityParser.toModel(data.identity),
    returnTo: data.return_to,
  }),
};
