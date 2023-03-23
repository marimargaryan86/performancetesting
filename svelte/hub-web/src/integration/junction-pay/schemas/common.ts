export interface RelationshipSchema<T extends { id: string; type: string }> {
  data: T;
}
