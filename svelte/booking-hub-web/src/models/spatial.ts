export type DirectionY = "up" | "down";

export type DirectionX = "left" | "right";

export type Direction = DirectionY | DirectionX;

export interface PointModel {
  ref: string;
  name: string;
  latitude: number;
  longitude: number;
  timeZone: string;
}
