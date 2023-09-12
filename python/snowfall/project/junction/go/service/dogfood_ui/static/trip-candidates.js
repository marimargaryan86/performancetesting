function load_trip_candidates(id) {
  fetch("/trip-candidates/searches/" + id)
    .then((res) => res.json())
    .then((response) => {
      if (
        response.data.attributes.status == "completed" ||
        response.data.attributes.status == "failed"
      ) {
        fetch(
          "/trip-candidates/searches/" +
            id +
            "/offers?page[limit]=100&include=groups,groups.details,groups.details.legType"
        )
        .then((res) => res.json())
        .then((response) => {
          inject_trips(id, transform_trip_candidates(response), false);
        });
      } else {
        setTimeout(() => {
          load_trip_candidates(id);
        }, "2000");
      }
    });
}

function transform_trip_candidates(response) {
  trips = [];
  segments = [];
  legs = [];
  included = {};

  if (response.data.length == 0) {
    return {
      "data": [],
      "included": [],
    }
  }

  for (const resource of response.included) {
    included[resource.type + resource.id] = resource;
  }

  for (const [i, resource] of response.data.entries()) {
    candidate = flatten(resource, included);

    segment_ids = [];

    for (const [j, group] of candidate.relationships.groups.data.entries()) {
      for (const [k, details] of group.relationships.details.data.entries()) {
        leg_ids = [];

        for (const [l, leg] of details.attributes.legs.entries()) {
            leg_id = group.id+l.toString()
            leg_ids.push({
              "id": leg_id,
              "type": "legs"
            })

            legs.push(
              {
                "id": leg_id,
                "type": "legs",
                "attributes": {
                  "departureAt": leg.departureAt,
                  "arrivalAt": leg.arrivalAt,
                  "origin": leg.origin,
                  "destination": leg.destination
                },
                "relationships": {
                  "legType": details.relationships.legType
                }
              }
            )
        }


        segment_ids.push({
          "id": details.id,
          "type": "segments"
        })

        segments.push(
          {
            "id": details.id,
            "type": "segments",
            "attributes": {
              "name": details.attributes.vendor,
              "operator": details.attributes.operator
            },
            "relationships": {
              "legs": {
                "data": leg_ids
              }
            }
          }
        )
      }
    }

    trips.push(
      {
        "id": candidate.id,
        "type": "trips",
        "attributes": {},
        "relationships": {
          "segments": {
            "data": segment_ids,
          }
        }
      }
    )
  }

  response.included.push(...segments)
  response.included.push(...legs)

  return {
    "data": trips,
    "included": response.included,
  }
}
