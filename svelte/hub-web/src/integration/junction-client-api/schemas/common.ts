export interface RelationshipSchema<
  T extends { id: string; type: string } | { id: string; type: string }[],
> {
  data: T;
}

export interface PointSchema {
  ref: string;
  name: string;
  latitude: number;
  longitude: number;
  timeZone: string;
}
