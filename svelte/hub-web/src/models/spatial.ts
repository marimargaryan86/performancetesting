import type { CoordinatesModel } from "./booking/location";

export type DirectionY = "up" | "down";

export type DirectionX = "left" | "right";

export type Direction = DirectionY | DirectionX;

export interface PointModel {
  ref: string;
  name: string;
  coordinates: CoordinatesModel;
  timeZone: string;
}
