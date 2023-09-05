import {
  offerModel,
  offerGroupModel,
  legTypeModel,
  cabinClassModel,
  tripOfferOptionDetailsModel,
  offerOptionModel,
  tripOfferGroupDetailsModel,
  tripOfferPriceQuoteModel,
} from "../schemas/offer";
import type { Infer } from "../schema-model.server";
import { ensureDefined } from "utils/array";

export function parseOfferGroupDetailsSchema(
  data: Infer<typeof tripOfferGroupDetailsModel, "schema">,
  included: { legTypes: Infer<typeof legTypeModel>[] },
): Infer<typeof tripOfferGroupDetailsModel> {
  return {
    ...tripOfferGroupDetailsModel.toModel(data),
    legType: included.legTypes.find((item) => item.id === data.relationships.legType.data.id),
  };
}

export function parseOfferOptionDetailsSchema(
  data: Infer<typeof tripOfferOptionDetailsModel, "schema">,
  included: { cabinClasses: Infer<typeof cabinClassModel>[] },
): Infer<typeof tripOfferOptionDetailsModel> {
  return {
    ...tripOfferOptionDetailsModel.toModel(data),
    cabinClass: included.cabinClasses.find(
      (item) => item.id === data.relationships.cabinClass.data.id,
    ),
  };
}

export function parseOfferOptionSchema(
  data: Infer<typeof offerOptionModel, "schema">,
  included: { offerOptionDetails: Infer<typeof tripOfferOptionDetailsModel>[] },
): Infer<typeof offerOptionModel> {
  return {
    ...offerOptionModel.toModel(data),
    details: data.relationships.details.data
      .map((item) => included.offerOptionDetails.find((item2) => item.id === item2.id))
      .filter(ensureDefined),
  };
}

export function parseOfferGroupSchema(
  data: Infer<typeof offerGroupModel, "schema">,
  included: {
    offerOptions: Infer<typeof offerOptionModel>[];
    offerGroupDetails: Infer<typeof tripOfferGroupDetailsModel>[];
  },
): Infer<typeof offerGroupModel> {
  return {
    ...offerGroupModel.toModel(data),
    options: data.relationships.options.data
      .map((item) => included.offerOptions.find((item2) => item.id === item2.id))
      .filter(ensureDefined),
    details: data.relationships.details.data
      .map((item) => included.offerGroupDetails.find((item2) => item.id === item2.id))
      .filter(ensureDefined),
  };
}

export function parseOfferSchema(
  data: Infer<typeof offerModel, "schema">,
  included: { offerGroups: Infer<typeof offerGroupModel>[] },
): Infer<typeof offerModel> {
  return {
    ...offerModel.toModel(data),
    groups: data.relationships.groups.data
      .map((item) => included.offerGroups.find((item2) => item.id === item2.id))
      .filter(ensureDefined),
  };
}

export function parsePriceQuoteSchema(
  data: Infer<typeof tripOfferPriceQuoteModel, "schema">,
  included: { offers: Infer<typeof offerModel>[] },
): Infer<typeof tripOfferPriceQuoteModel> {
  const parsed = tripOfferPriceQuoteModel.toModel(data);
  const offer = included.offers.find((item) => item.id === data.relationships.offer.data.id);
  const options = Array.from(
    new Set(
      offer?.groups.flatMap((group) =>
        group.options.filter((item) => parsed.optionIds.includes(item.id)),
      ) ?? [],
    ),
  );

  return { ...parsed, offer, options };
}
