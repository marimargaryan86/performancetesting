export type LegType = {
  id: "unspecified" | "air" | "rail";
  name: string;
};

export type LegTypeSchema = {
  id: "unspecified" | "air" | "rail";
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
