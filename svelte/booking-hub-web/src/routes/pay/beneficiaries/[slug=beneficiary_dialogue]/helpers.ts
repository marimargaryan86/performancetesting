import type { CreateBeneficiaryModel } from "models/beneficiary";

function lengthOrUndefined(item?: string): string | undefined {
  const nextItem = item?.trim();

  return nextItem?.length ? nextItem : undefined;
}

export function updateBeneficiaryData(data: CreateBeneficiaryModel): CreateBeneficiaryModel {
  return {
    ...data,
    email: lengthOrUndefined(data.email),
    companyName: lengthOrUndefined(data.companyName),
    address: {
      ...data.address,
      addressLines: data.address?.addressLines?.map((al) => al.trim()),
      city: lengthOrUndefined(data.address?.city),
      countryCode: lengthOrUndefined(data.address?.countryCode),
      postalCode: lengthOrUndefined(data.address?.postalCode),
      state: lengthOrUndefined(data.address?.state),
    },
    currencyCode: lengthOrUndefined(data.currencyCode),
    bankDetails: {
      ...data.bankDetails,
      accountType: "checking",
      address: {
        ...data.bankDetails.address,
        addressLines: data.bankDetails.address?.addressLines?.map((al) => al.trim()),
        countryCode: lengthOrUndefined(data.bankDetails.address?.countryCode),
      },
      bicSwift: lengthOrUndefined(data.bankDetails.bicSwift),
      name: lengthOrUndefined(data.bankDetails.name),
      paymentType: data.bankDetails.paymentType,
      ...(data.bankDetails.type === "aba"
        ? {
            ...data.bankDetails,
            type: "aba",
            aba: lengthOrUndefined(data.bankDetails.aba),
            accountNumber: lengthOrUndefined(data.bankDetails.accountNumber),
          }
        : {
            ...data.bankDetails,
            type: "iban",
            iban: lengthOrUndefined(data.bankDetails.iban),
          }),
    },
  };
}
