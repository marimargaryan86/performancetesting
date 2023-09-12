import type { OrderModel } from "models/order";
import type { JourneySchema } from "../schemas/journey";
import type { OrderSchema } from "../schemas/order";

export function parseOrder(order: OrderSchema, journeys: JourneySchema[]): OrderModel {
  return {
    passengers: order.attributes.passengers.map((item) => ({
      dateOfBirth: new Date(item.dateOfBirth),
      firstName: item.firstName,
      gender: item.gender,
      lastName: item.lastName,
      title: item.title,
      travelerDocument: item.travelerDocument
        ? {
            expirationDate: item.travelerDocument.documentExpirationDate
              ? new Date(item.travelerDocument.documentExpirationDate)
              : undefined,
            issueCountry: item.travelerDocument.documentIssueCountry,
            issueDate: item.travelerDocument.documentIssueDate
              ? new Date(item.travelerDocument.documentIssueDate)
              : undefined,
            nationality: item.travelerDocument.nationality,
            number: item.travelerDocument.documentNumber,
            residenceCountryCode: item.travelerDocument.residenceCountryCode,
            type: item.travelerDocument.documentType,
          }
        : undefined,
    })),
    journeys: journeys.map((item) => ({
      reference: item.attributes.reference,
      contact: {
        address: {
          addressLines: item.attributes.contactDetails.address.addressLines.filter(
            (line) => line.length,
          ),
          city: item.attributes.contactDetails.address.city,
          countryCode: item.attributes.contactDetails.address.countryCode,
          postalCode: item.attributes.contactDetails.address.postalCode,
        },
        email: item.attributes.contactDetails.email,
        phoneNumber: item.attributes.contactDetails.phoneNumber,
      },
    })),
  };
}
