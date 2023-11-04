export type LegType = {
  id: string;
  name: string;
};

export type LegTypeSchema = {
  id: string;
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
