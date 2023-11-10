import {
  tripCandidateSearchParser,
  type TripCandidateSearch,
  type TripCandidateSearchSchema,
  type TripCandidateSearchCreate,
  type TripCandidateSearchCreateSchema,
} from "./trip-candidate";

export type SimpleOfferSearch = TripCandidateSearch;

export type SimpleOfferSearchSchema = Omit<TripCandidateSearchSchema, "type"> & {
  type: "simple-offer-searches";
};

export type SimpleOfferSearchCreate = TripCandidateSearchCreate;

export type SimpleOfferSearchCreateSchema = Omit<TripCandidateSearchCreateSchema, "type"> &
  Pick<SimpleOfferSearchSchema, "type">;

export const simpleOffserSearchParser = {
  toModel: (data: SimpleOfferSearchSchema): SimpleOfferSearch => ({
    ...tripCandidateSearchParser.toModel({ ...data, type: "trip-candidate-searches" }),
  }),
  toCreateSchema: (data: SimpleOfferSearchCreate): SimpleOfferSearchCreateSchema => ({
    ...tripCandidateSearchParser.toCreateSchema({ ...data }),
    type: "simple-offer-searches",
  }),
};
