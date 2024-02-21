export const transportTypes = ["unspecified", "air", "rail", "car"] as const;
export type TransportType = (typeof transportTypes)[number];
export type LegType = {
  id: TransportType;
  name: string;
};

export type LegTypeSchema = {
  id: TransportType;
  type: "leg-types";
  attributes: {
    name: string;
  };
  links: { self: string };
};

export const legTypeParser = {
  toModel: (data: LegTypeSchema): LegType => ({
    id: data.id,
    name: data.attributes.name,
  }),
};
