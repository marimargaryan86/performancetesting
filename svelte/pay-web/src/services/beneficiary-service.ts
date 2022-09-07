import { undefinedIfZeroLength } from "$helpers/string-helpers";
import type {
  BeneficiaryModel,
  BeneficiaryPutModel,
} from "$integration/currency-cloud/models/beneficiaries/common";
import type { RequirementsModel } from "$integration/currency-cloud/models/beneficiaries/requirements";
import type { RecursivePartial, ValidationError } from "$integration/currency-cloud/models/common";
import type { PaymentType } from "$integration/currency-cloud/schemas/beneficiaries";
import utils from "$lib/utils";
import type { CreateBeneficiarySchema } from "src/routes/api/schemas/beneficiaries";

export default class BeneficiaryService {
  async getRequirements(
    bankAccountCountryCode: string,
    bankAccountCurrencyCode: string,
    contactAccountCountryCode?: string,
    entityType?: string,
    paymentTypes?: PaymentType[],
  ): Promise<RequirementsModel[]> {
    return await (
      await fetch(
        utils.buildUrl(new URL("/api/beneficiaries/requirements", window.location.origin), {
          bankAccountCountryCode,
          bankAccountCurrencyCode,
          contactAccountCountryCode,
          entityType,
          paymentTypes: paymentTypes && paymentTypes.length ? paymentTypes.join(",") : undefined,
        }),
      )
    ).json();
  }

  async find(criteria?: { offset?: number; limit?: number }): Promise<BeneficiaryModel[]> {
    const offset = criteria?.offset ?? 0;
    const limit = criteria?.limit ?? 20;

    const resp = await fetch(
      utils.buildUrl(new URL("/api/beneficiaries", window.location.origin), {
        "orderBy[asc]": "nickname",
        "page[limit]": limit,
        "page[offset]": offset,
      }),
    );

    const respData = await resp.json();

    if (resp.status === 200) {
      return respData; // TODO: Parse.
    }

    return [];
  }

  async remove(id: string): Promise<void> {
    await fetch(new URL(`/api/beneficiaries/${id}`, window.location.origin), {
      method: "DELETE",
    });
  }

  async create(data: RecursivePartial<BeneficiaryPutModel>): Promise<BeneficiaryModel> {
    const parsedData: RecursivePartial<CreateBeneficiarySchema> = {
      nickname: undefinedIfZeroLength(data.nickname?.trim()),
      bank: {
        account: {
          currencyCode: undefinedIfZeroLength(data.bank?.account?.currencyCode?.trim()),
          holderName: undefinedIfZeroLength(data.bank?.account?.holderName?.trim()),
          bic: undefinedIfZeroLength(data.bank?.account?.bic?.trim()),
          iban: undefinedIfZeroLength(data.bank?.account?.iban?.trim()),
          number: undefinedIfZeroLength(data.bank?.account?.number?.trim()),
          sortCode: undefinedIfZeroLength(data.bank?.account?.sortCode?.trim()?.replace(/-/g, "")),
        },
        countryCode: undefinedIfZeroLength(data.bank?.countryCode?.trim()),
      },
      contact: {
        address: undefinedIfZeroLength(data.contact?.address?.trim()),
        city: undefinedIfZeroLength(data.contact?.city?.trim()),
        countryCode: undefinedIfZeroLength(data.contact?.countryCode?.trim()),
        postalCode: undefinedIfZeroLength(data.contact?.postalCode?.trim()),
        stateOrProvince: undefinedIfZeroLength(data.contact?.stateOrProvince?.trim()),
        email: undefinedIfZeroLength(data.contact?.email?.trim()),
      },
      paymentTypes: undefinedIfZeroLength(data.paymentTypes),
      entityType: undefinedIfZeroLength(data.entityType),
      company:
        data.entityType === "company"
          ? {
              name: undefinedIfZeroLength(data.company?.name?.trim()),
              registrationDate: undefinedIfZeroLength(
                data.company?.registrationDate?.toLocaleDateString("sv-SE"),
              ),
            }
          : undefined,
      individual:
        data.entityType === "individual"
          ? {
              firstName: undefinedIfZeroLength(data.individual?.firstName?.trim()),
              lastName: undefinedIfZeroLength(data.individual?.lastName?.trim()),
              birthDate: undefinedIfZeroLength(
                data.individual?.birthDate?.toLocaleDateString("sv-SE"),
              ),
            }
          : undefined,
    };

    const resp = await fetch(new URL("/api/beneficiaries", window.location.origin), {
      method: "POST",
      body: JSON.stringify(parsedData),
      headers: { "Content-Type": "application/json" },
    });

    const respData = await resp.json();

    if (resp.status === 201) {
      return respData;
    }

    if (resp.status === 400) {
      throw "BAD_REQUEST";
    }

    if (resp.status === 422) {
      const error = respData.detail;

      if (error instanceof Array) {
        throw error.reduce<ValidationError<BeneficiaryPutModel>>(
          (prev, curr: ValidationError<BeneficiaryPutModel>) => {
            const prevCompany = (prev as ValidationError<BeneficiaryPutModel<"company">>)?.company;
            const prevIndividual = (prev as ValidationError<BeneficiaryPutModel<"individual">>)
              ?.individual;
            const currCompany = (curr as ValidationError<BeneficiaryPutModel<"company">>)?.company;
            const currIndividual = (curr as ValidationError<BeneficiaryPutModel<"individual">>)
              ?.individual;

            return {
              bank: {
                account: {
                  bic: curr?.bank?.account?.bic ?? prev?.bank?.account?.bic,
                  currencyCode:
                    curr?.bank?.account?.currencyCode ?? prev?.bank?.account?.currencyCode,
                  holderName: curr?.bank?.account?.holderName ?? prev?.bank?.account?.holderName,
                  iban: curr?.bank?.account?.iban ?? prev?.bank?.account?.iban,
                  number: curr?.bank?.account?.number ?? prev?.bank?.account?.number,
                  sortCode: curr?.bank?.account?.sortCode ?? curr?.bank?.account?.sortCode,
                  type: curr?.bank?.account?.type ?? prev?.bank?.account?.type,
                },
                address: curr?.bank?.address ?? prev?.bank?.address,
                countryCode: curr?.bank?.countryCode ?? prev?.bank?.countryCode,
                name: curr?.bank?.name ?? prev?.bank?.name,
              },
              company: {
                name: currCompany?.name ?? prevCompany?.name,
                registrationDate: currCompany?.registrationDate ?? prevCompany?.registrationDate,
              },
              individual: {
                firstName: currIndividual?.firstName ?? prevIndividual?.firstName,
                lastName: currIndividual?.lastName ?? prevIndividual?.lastName,
                birthDate: currIndividual?.birthDate ?? prevIndividual?.birthDate,
              },
              contact: {
                address: curr?.contact?.address ?? prev?.contact?.address,
                city: curr?.contact?.city ?? prev?.contact?.city,
                countryCode: curr?.contact?.countryCode ?? prev?.contact?.countryCode,
                email: curr?.contact?.email ?? prev?.contact?.email,
                postalCode: curr?.contact?.postalCode ?? prev?.contact?.postalCode,
                externalReference:
                  curr?.contact?.externalReference ?? prev?.contact?.externalReference,
                stateOrProvince: curr?.contact?.stateOrProvince ?? prev?.contact?.stateOrProvince,
              },
              default: curr?.default ?? prev?.default,
              entityType: curr?.entityType ?? prev?.entityType,
              identification: {
                type: curr?.identification?.type ?? prev?.identification?.type,
                value: curr?.identification?.value ?? prev?.identification?.value,
              },
              nickname: curr?.nickname ?? prev?.nickname,
              onBehalfOf: curr?.onBehalfOf ?? prev?.onBehalfOf,
              paymentTypes: curr?.paymentTypes ?? prev?.paymentTypes,
            };
          },
          {},
        );
      }

      throw error;
    }

    return respData; // TODO: Parse.
  }
}
