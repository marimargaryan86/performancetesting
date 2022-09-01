import type { OrderField } from "$integration/currency-cloud/models/accounts";
import type {
  AccountStatus,
  AccountVerificationStatus,
} from "$integration/currency-cloud/schemas/accounts";

export type FindCriteriaSchema = {
  name?: string;
  brand?: string;
  ref?: string;
  status?: AccountStatus;
  contactAddress?: string;
  contactPostalCode?: string;
  contactCity?: string;
  contactStateOrProvince?: string;
  contactCountryCode?: string;
  spreadTable?: string;
  bankAccountVerificationStatus?: AccountVerificationStatus;
  "page[offset]"?: number;
  "page[limit]"?: number;
  "orderBy[asc]"?: OrderField;
  "orderBy[desc]"?: OrderField;
};
