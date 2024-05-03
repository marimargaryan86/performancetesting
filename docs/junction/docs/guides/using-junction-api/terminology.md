---
sidebar_position: 1
---

# Key Concepts

These are key terms referenced throughout the documentation that will be handy to know.

## Terms to know for your first search

A `leg` is the part between two stops traversed by the same vehicle. A leg is always within a segment.

A `segment` is a part of the trip that you travel using the same vehicle (e.g. a flight or a train). The segment can be a direct service or have stops, we indicate the parts between these stops as legs.

A `trip` connects any two places and represents the complete end-to-end journey between an origin and destination. A trip is composed by one or multiple segments.

A `place` is a city, airport, railway station, bus station, or ferry port, that can serve as an origin or destination. We connect places by using a trip.

## Terms to know when selecting a Trip

A `quote` provides an accurate price for the selected combination of offer options within an offer. An offer option for each offer group within an offer is required. This step is required before creating an order.

Given a segment for a trip can have multiple ways of getting from an origin to a destination with different start and end points - each offer contains offer groups and offer options.

An `offer group` is a collection of price points (offer options) for one segment of a trip.

Example:
A direct flight would be one offer group. A one stop flight with a change of aircraft would be two offer groups.

An `offer option` is a singular price point for an offer group.

Example:
A direct flight on economy for $200

Or

A direct flight on business for $350

A `Trip Candidate` is a searchable criteria which finds and prices trips. These priced trips are also known as `offers` and contain distinct options from which the user can choose from to satisfy a given trip.

## Terms to know when creating an order

A `booking` is the atomic unit. It covers a booking for one segment of the offer.

    Example: Rail booking

An `order` is a container of one or multiple bookings. An order exists at the same level as a Trip-Candidate.

    Example:
    1 order = (1 Flight booking) + (1 rail booking)

A `journey` is a container of one or multiple orders (This is for advanced use-cases).

    Example:
    1 journey = (1 flight + rail order) + (1 car rental order)
