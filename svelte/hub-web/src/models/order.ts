export interface OrderPassengerModel {
  firstName: string;
  lastName: string;
  title: "unspecified" | "mr" | "mrs" | "ms" | "miss";
  gender: "unspecified" | "male" | "female";
  dateOfBirth: Date;
  travelerDocument?: {
    type?: "passport";
    number?: string;
    issueCountry?: string;
    expirationDate?: Date;
    issueDate?: Date;
    nationality?: string;
    residenceCountryCode?: string;
  };
}

export interface JourneyModel {
  reference: string;
  contact: {
    email: string;
    address: {
      addressLines: string[];
      countryCode: string;
      postalCode: string;
      city: string;
    };
    poneNumber: string;
  };
}

export interface OrderModel {
  passengers: OrderPassengerModel[];
  journeys: JourneyModel[];
}
