# Getting Started

Before you search and book a trip through Junction you need to understand a few important key concepts.

## Key Concepts

### Trips, Segments and Legs

A journey between your origin and your destination is referred to as a **Trip**. A trip has one or multiple **Segments**, where the definition of a segment is a part of the trip that you travel using the same vehicle (e.g. a flight or a train). A segment can then split up even further into one or multiple **Legs**, where one leg is the part between two stops said vehicle does during a segment.

As an example; if you travel from **Uppsala C** to **London Heathrow Airport** your trip will consist of two **Segments**. Your first segment will be your train between _Uppsala C_ and _Arlanda C_ and that consists of two **Legs**; _Uppsala C_ to _Knivsta C_, followed by _Knivsta C_ to _Arlanda C_. Then, after a short transfer on foot to your terminal at _Stockholm Arlanda Airport_, your second and final segment will be one leg between _Stockholm Arlanda Airport_ and _London Heathrow Airport_ (your final destination).

To search for **Trips** between point A and point B, you create a **Trip Search** using two **Places** to state your desired origin and destination. During a **Trip Search**, Junction tries to find the most efficient trips throughout the day using schedules from its connected operators. The **Trip Search** is an _asynchronous_  process and it could take several seconds before any trips become available.

### Offers

Once you have found a trip you want to book, you need to do an **Offer Search** for it. During an **Offer Search**, Junction sends optimized fragments of your trip off to its connected providers to find out if they're offering that particular fragment and at what price. An **Offer Search** is, just like the **Trip Search**, an _asynchronous_  process and it could take several seconds before any offers become available.

An offer consists of three parts; the offer aggregate, the offer groups and the offers themselves. An offer aggregate is a collection of offer groups that together can offer your entire trip. Each offer group covers one or multiple segments of your trip, and each offer group has one or multiple offers for that particular group.

As an example; if you're searching for offers for a trip from **Uppsala C** to **London Heathrow Airport**, you could get an offer aggregate back with two offer groups; one group with offers for the rail segment between _Uppsala C_ and _Arlanda C_ from SJ, and one group with offers for the air segment between _Stockholm Arlanda Airport_ and _London Heathrow Airport_ with SAS.

Taking a look at each group, the first group could contain two offers; one for First Class and one for Second Class; while the second group could contain two offers; one for SAS Go and one for SAS Plus.

### Orders

Once you've decided on an offer aggregate you want to book, you'll need to create an **Order** by passing your offer aggregate of choice, including one offer from each of its offer groups, as well as passenger and contact details (first names, last names, dates of birth etc.). Creating an **Order** is, just like the **Trip Search** and **Order Search**, an _asynchronous_  process and it could take several seconds before your order is finalised.

## Definitions

### Place
An indexed location in the world that Junction might have content for, such as airports, rail stations, hotels etc. Its main use is to specify origin and destination in a **Trip Search**.

For more information about **Place**, see its [API schema definition](../../openapi/junction/client_api/openapi.json/components/schemas/Place).

### Trip
A journey between two **Points**, an origin and a destination. A trip is made up of one or multiple **Segments**, and each segment is made up of one or multiple **Legs**.

For more information about **Trip**, see its [API schema definition](../../openapi/junction/client_api/openapi.json/components/schemas/Trip).

### Segment
The element of the trip between a boarding point and and an disembarking point within the same mode of travel. A segment is a collection of legs.
The trip from one place to another that may contain multiple segments to get from an origin place to the destination place.

For more information about **Segment**, see its [API schema definition](../../openapi/junction/client_api/openapi.json/components/schemas/Segment).

### Leg
A single element of the trip segment carried by a provider.
The operation between two consecutive scheduled stops on any given flight/rail/car/bus.

For more information about **Leg**, see its [API schema definition](../../openapi/junction/client_api/openapi.json/components/schemas/Leg).

### Offer Aggregate
A collection of offers that together covers your entire trip.

For more information about **Offer Aggregate**, see its [API schema definition](../../openapi/junction/client_api/openapi.json/components/schemas/OfferAggregate).

### Offer Group
A collection of offers within an offer aggregate that covers the same segment(s) and are all related to each other (e.g. sold by the same provider but with different cabin classes, baggage allowances etc.).

For more information about **Offer Group**, see its [API schema definition](../../openapi/junction/client_api/openapi.json/components/schemas/OfferGroup).

### Offer
A priced offer for one or multiple segments of a trip with a defined set of attributes (cabin class, baggage allowance etc.).

For more information about **Offer**, see its [API schema definition](../../openapi/junction/client_api/openapi.json/components/schemas/Offer).

### Order

A booking that contains information about purchased offers. It can, once created, be extended with additional offers if needed.

For more information about **Order**, see its [API schema definition](../../openapi/junction/client_api/openapi.json/components/schemas/Order).
