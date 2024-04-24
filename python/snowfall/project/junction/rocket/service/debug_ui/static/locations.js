async function load_locations(ids) {
  let locations = []
  let page_token = ""

  while (true) {
    const response = await (await fetch("/locations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ids: {
          ids: ids,
        },
        pageToken: page_token,
      }),
    })).json()

    for (const location of response.locations) {
      locations.push(location)
    }

    if (response.locations.length > 0) {
      page_token = response.nextPageToken
    } else {
      break
    }
  }

  return locations
}

async function find_location(lat, long) {
  const response = await (await fetch("/locations/near", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      coordinates: {
        latitude: lat,
        longitude: long
      },
      precision: {
        "mode": "MODE_AREA",
      },
    }),
  })).json()

  const locations = response.locations.sort((a, b) => {
    const aDistance = getDistanceFromLatLonInKm(lat, long, a.coordinates.latitude, a.coordinates.longitude)
    const bDistance = getDistanceFromLatLonInKm(lat, long, b.coordinates.latitude, b.coordinates.longitude)

    return aDistance-bDistance
  })

  return locations[0]
}

function getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2) {
  var R = 6371; // Radius of the earth in km
  var dLat = deg2rad(lat2-lat1);  // deg2rad below
  var dLon = deg2rad(lon2-lon1);
  var a =
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(deg2rad(lat1)) * Math.cos(deg2rad(lat2)) *
    Math.sin(dLon/2) * Math.sin(dLon/2)
    ;
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  var d = R * c; // Distance in km
  return d;
}

function deg2rad(deg) {
  return deg * (Math.PI/180)
}
