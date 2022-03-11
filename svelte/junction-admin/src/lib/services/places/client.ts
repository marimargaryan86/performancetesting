import type { CoordinatesModel } from '$lib/models/common';
import type { PlaceModel } from '$lib/models/place';
import BaseClient from '../base-client';

export type SearchData = {
	name?: string;
	coordinates?: CoordinatesModel;
	proximity: number;
};

export default class PlaceClient extends BaseClient {
	async getPlaces(data: SearchData): Promise<PlaceModel[]> {
		try {
			console.log(data);

			return [
				{
					coordinates: {
						latitude: 43.4,
						longitude: 55.1
					},
					countryCode: 'SE',
					id: 'identifier-0',
					name: 'Uppsala Centralstation',
					sourceRef: 'source-reference-0',
					timeZone: 'SE',
					updatedAt: new Date('2018-01-23')
				}
			];
		} catch (error) {
			//
		}
	}
}
