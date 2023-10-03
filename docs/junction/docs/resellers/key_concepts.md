---
sidebar_position: 3
---

# Key Concepts

You'll need to understand the terminology in order to get started with finding and booking trips using the Junction Reseller API.

## Trips, Segments and Legs

A journey between your origin and your destination is referred to as a **Trip**.
A trip has one or multiple **Segments**, where the definition of a segment is a
part of the trip that you travel using the same vehicle (e.g. a flight or a
train). A segment can then split up even further into one or multiple **Legs**,
where one leg is the part between two stops said vehicle does during a segment.

As an example; if you travel from **Uppsala C** to **London Heathrow Airport**
your trip will consist of two **Segments**. Your first segment will be your train
between _Uppsala C_ and _Arlanda C_ and that consists of two **Legs**; _Uppsala C_
to _Knivsta C_, followed by _Knivsta C_ to _Arlanda C_. Then, after a short
transfer on foot to your terminal at _Stockholm Arlanda Airport_, your second
and final segment will be one leg between _Stockholm Arlanda Airport_ and
_London Heathrow Airport_ (your final destination).

To search for **Trips** between point A and point B, you create a **Trip Search**
using two **Places** to state your desired origin and destination. During a
**Trip Search**, Junction tries to find the most efficient trips throughout the
day using schedules from its connected operators. The **Trip Search** is an
_asynchronous_ process and it could take several seconds before any trips
become available.

## Offers, Offer Groups and Offer Options

Once you have found a trip you want to book, you need to do an **Offer Search**
for it. During an **Offer Search**, Junction sends optimized fragments of your
trip off to its connected providers to find out if they're offering that
particular fragment and at what price. An **Offer Search** is, just like the
**Trip Search**, an _asynchronous_ process and it could take several seconds
before any offers become available.

An offer consists of two parts; the offer groups and the
offer options. An offer is a collection of offer groups that
together can offer your entire trip. Each offer group covers one or multiple
segments of your trip with the same provider, and each offer group has one or multiple offer options for that
particular group.

As an example; if you're searching for offers for a trip from **Uppsala C** to
**London Heathrow Airport**, you could get an offer back with two
offer groups; one group with offer options for the rail segment between _Uppsala C_ and
_Arlanda C_, and one group with offer options for the air segment between
_Stockholm Arlanda Airport_ and _London Heathrow Airport_.

Taking a look at each group, the first group could contain two offer options; one for
Airline 1 Business and one for Airline 1 Economy; while the second group could contain two
offer options; one for Airline 2 Business and one for Airline 2 Economy.

One offer group can appear in multiple offers, see the following diagram:

<img src="/img/offer-aggregates.jpg" width="600"/>

## Quotes

Price quotes provide an accurate price for the chosen combination of offer options within an offer.
Creating a price quote is required before placing an order.
To create a valid price quote for placing an order you have to include an offer option for each offer group in an offer.

## Journeys, Orders, Bookings

Once you've decided on an offer you want to book, you'll need to
create an **Order** by passing your price quote, as well as passenger and contact details
(first names, last names, dates of birth etc.). Creating an **Order** is, just
like the **Trip Search** and **Order Search**, an _asynchronous_ process and it
could take several seconds before your order is finalised.

A Journey represents an itinerary for a group of passengers, functioning as a placeholder (container) for Orders.
Each order consists of one or multiple provider Bookings.
Once a Journey is in place, new Orders could be added to it, or existing ones changed.

Booking represents one atomic unit booked from some Provider of travel or travel-related content.
It contains a reference that can usually be used with Provider's systems to verify and manage Booking content.
For example, in case of trip booking for a flight, that external reference is airline PNR ("passenger name record").
A successful booking has a status of either `confirmed` or `not_ticketed`.
