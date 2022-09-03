import type { BeneficiaryModel, BeneficiaryPutModel } from "../models/beneficiaries/common";
import type { FindCriteriaModel } from "../models/beneficiaries/find";
import type { GetRequirementsModel, RequirementsModel } from "../models/beneficiaries/requirements";
import type { RecursivePartial } from "../models/common";
import {
  parseBeneficiarySchema,
  parseBeneficiaryPutModel,
  updateBeneficiaryModel,
} from "../parsers/beneficiaries";
import { parseFindCriteriaModel } from "../parsers/beneficiaries";
import { parseGetRequirementsModel, parseRequirementsSchema } from "../parsers/beneficiaries";
import type {
  BeneficiarySchema,
  FindBeneficiariesResponseSchema,
  GetRequirementsSchema,
  RequirementsResponseSchema,
} from "../schemas/beneficiaries";
import { validatePutModel } from "../validators/beneficairy";
import { validateUUID } from "../validators/common";
import BaseService from "./base-service";

export enum BeneficiaryServiceError {
  NOT_FOUND = 0,
  SERVICE_UNAVAILABLE = 1,
  INVALID_BENEFICIARY = 2,
  INVALID_REQUIREMENTS_CRITERIA = 3,
}

export default class BeneficiaryService extends BaseService {
  async find(criteria: FindCriteriaModel): Promise<BeneficiaryModel[]> {
    const resp = await this.fetch(
      "/v2/beneficiaries/find",
      undefined,
      parseFindCriteriaModel(criteria),
    );

    switch (resp.status) {
      case 200:
        break;
      default:
        throw BeneficiaryServiceError.SERVICE_UNAVAILABLE;
    }

    const data: FindBeneficiariesResponseSchema = await resp.json();

    return data.beneficiaries.map((item) => parseBeneficiarySchema(item));
  }

  async create(beneficiary: BeneficiaryPutModel): Promise<BeneficiaryModel> {
    return this.put(beneficiary);
  }

  async update(
    id: string,
    updateData: RecursivePartial<BeneficiaryPutModel>,
  ): Promise<BeneficiaryModel> {
    const beneficiary = await this.get(id);
    const updated = updateBeneficiaryModel(beneficiary, updateData);

    return this.put(updated, beneficiary);
  }

  async get(id: string): Promise<BeneficiaryModel> {
    const errors = validateUUID(id);

    if (errors) {
      throw errors;
    }

    const resp = await this.fetch(`/v2/beneficiaries/${id}`);

    switch (resp.status) {
      case 200:
        break;
      case 404:
        throw BeneficiaryServiceError.NOT_FOUND;
      default:
        throw BeneficiaryServiceError.SERVICE_UNAVAILABLE;
    }

    const data: BeneficiarySchema = await resp.json();

    return parseBeneficiarySchema(data);
  }

  async remove(id: string): Promise<void> {
    const errors = validateUUID(id);

    if (errors) {
      throw errors;
    }

    const resp = await this.fetch(`/v2/beneficiaries/${id}/delete`, { method: "POST" });

    switch (resp.status) {
      case 200:
        break;
      case 404:
        throw BeneficiaryServiceError.NOT_FOUND;
      default:
        throw BeneficiaryServiceError.SERVICE_UNAVAILABLE;
    }
  }

  private async put(
    beneficiary: BeneficiaryPutModel,
    oldBeneficiary?: BeneficiaryModel,
  ): Promise<BeneficiaryModel> {
    if (oldBeneficiary) {
      beneficiary = updateBeneficiaryModel(oldBeneficiary, beneficiary);
    }

    const requirementsList = await this.getRequirements({
      bank: {
        account: {
          countryCode: beneficiary.bank.countryCode,
          currencyCode: beneficiary.bank.account.currencyCode,
        },
      },
      contact: {
        countryCode: beneficiary.contact?.countryCode ?? undefined,
      },
      entityType: beneficiary.entityType ?? undefined,
      paymentTypes: beneficiary.paymentTypes,
    });

    const url = oldBeneficiary
      ? `/v2/beneficiaries/${oldBeneficiary.id}`
      : "/v2/beneficiaries/create";

    const resp = await this.fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(
        parseBeneficiaryPutModel(validatePutModel(beneficiary, requirementsList)),
      ),
    });

    let errors: { [key: string]: typeof errors };

    switch (resp.status) {
      case 200:
        break;
      case 400:
        errors = (await resp.json()).error_messages;

        throw {
          entityType: errors.beneficiary_entity_type ? ["Missing"] : undefined,
          bank: {
            account: {
              iban: errors.iban ? ["Invalid IBAN"] : undefined,
              bic: errors.bic_swift ? ["Invalid BIC"] : undefined,
            },
          },
        };
      default:
        throw BeneficiaryServiceError.SERVICE_UNAVAILABLE;
    }

    const data: BeneficiarySchema = await resp.json();

    return parseBeneficiarySchema(data);
  }

  async getRequirements(criteria: GetRequirementsModel): Promise<RequirementsModel[]> {
    const reqCriteria: GetRequirementsSchema = parseGetRequirementsModel(criteria);

    const resp = await this.fetch(
      "/v2/reference/beneficiary_required_details",
      undefined,
      reqCriteria,
    );

    switch (resp.status) {
      case 200:
        break;
      case 400:
        throw BeneficiaryServiceError.INVALID_REQUIREMENTS_CRITERIA;
      default:
        throw BeneficiaryServiceError.SERVICE_UNAVAILABLE;
    }

    const respData: RequirementsResponseSchema = await resp.json();

    return respData.details
      .map((item) => parseRequirementsSchema(item))
      .filter((item) => {
        return (
          (!criteria.entityType || item.entityType === criteria.entityType) &&
          (!criteria.paymentTypes || criteria.paymentTypes.includes(item.paymentType))
        );
      });
  }
}
