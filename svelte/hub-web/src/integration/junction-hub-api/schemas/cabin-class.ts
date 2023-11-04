export type CabinClass = {
  id: string;
  name: string;
};

export type CabinClassSchema = {
  id: string;
  type: "cabin-classes";
  attributes: {
    name: string;
  };
  links: { self: string };
};

export const cabinClassParser = {
  toModel: (data: CabinClassSchema): CabinClass => ({
    id: data.id,
    name: data.attributes.name,
  }),
};
