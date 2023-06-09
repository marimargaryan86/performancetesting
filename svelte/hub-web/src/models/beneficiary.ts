import type { AccountType, PaymentType } from "integration/junction-pay/schemas/beneficiaty";
import type { RecursivePartial } from "utils/common";

export type EnhancedAddressDetailsModel = {
  addressLines: string[];
  countryCode: string;
  postalCode?: string;
  city?: string;
  state?: string;
};

export type BankDetailsBaseModel = {
  name: string;
  bicSwift?: string;
  accountType: AccountType;
  paymentTypes: PaymentType;
  address: {
    addressLines: string[];
    countryCode: string;
  };
};

export type BankDetailsIbanModel = BankDetailsBaseModel & {
  type: "iban";
  iban?: string;
};

export type BankDetailsAbaModel = BankDetailsBaseModel & {
  type: "aba";
  accountNumber?: string;
  aba?: string;
};

export type BankDetailsModel = BankDetailsIbanModel | BankDetailsAbaModel;

export type BeneficiaryModel = {
  id: string;
  bankAccountHolderName: string;
  email: string;
  address: EnhancedAddressDetailsModel;
  bankDetails: BankDetailsModel;
  currencyCode: string;
  accountId: string;
};

export type CreateBeneficiaryModel = RecursivePartial<BeneficiaryModel>;
