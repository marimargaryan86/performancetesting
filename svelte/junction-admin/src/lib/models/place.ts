import type { CoordinatesModel } from './common';

export type PlaceModel = {
	id: string;
	name: string;
	coordinates: CoordinatesModel;
	timeZone: string;
	countryCode: string;
	updatedAt: Date;
	sourceRef: string;
};
