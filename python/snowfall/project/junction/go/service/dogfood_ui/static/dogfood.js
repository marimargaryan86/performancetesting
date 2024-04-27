dayjs.extend(window.dayjs_plugin_utc);
dayjs.extend(window.dayjs_plugin_timezone);

let db;

const icons = {
  air: "plane",
  rail: "train",
  bus: "bus",
  ferry: "ship",
  taxi: "taxi",
};

const greenIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});
const redIcon = new L.Icon({
  iconUrl:
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const uuidToName = {
  "4b7d12db-7735-4c67-9645-5fc82f7c4fe8": "ask2go",
  "f1f884bf-0be6-4ce2-8414-296a775a508d": "ba-ndc",
  "caefde65-c15c-4b60-b8d9-27638b50b08f": "benerail",
  "92ada881-f31c-471e-a8b0-01ed48a181d5": "direct-ferries",
  "30bfba87-7077-4d96-beed-c5769cdc99c7": "distribusion",
  "5d18e8e1-48e3-4b7c-82b9-62bd97a92f91": "duffel",
  "a5547dae-9c65-4746-8637-d0601865508e": "save-a-train",
  "f9ce75d1-2025-4ab5-b5d7-69e4c14c053e": "mock",
};

function getLang() {
  if (navigator.languages != undefined) return navigator.languages[0];
  return navigator.language;
}

function clear_places() {
  const transaction = db.transaction("places", "readwrite");
  const objectStore = transaction.objectStore("places");
  const clearRequest = objectStore.clear();

  clearRequest.onerror = (event) => {
    console.log(event);
  };
}

async function load_static_places() {
  const response = await fetch(staticPlacesFile).then((res) => res.json())

  for (const place of response) {
    const transaction = db.transaction("places", "readwrite");
    const objectStore = transaction.objectStore("places");
    let types = []

    for (const placeType of place.location.types) {
      switch (placeType) {
        case 0:
          types.push({"id": "unspecified","type": "place-types"})
          break
        case 1:
          types.push({"id": "city","type": "place-types"})
          break
        case 2:
          types.push({"id": "railway-station","type": "place-types"})
          break
        case 3:
          types.push({"id": "airport","type": "place-types"})
          break
        case 4:
          types.push({"id": "bus-station","type": "place-types"})
          break
        case 5:
          types.push({"id": "ferry-port","type": "place-types"})
          break
      }
    }

    const transformed = {
      id: place._id,
      type: "places",
      attributes: {
        countryCode: place.location.country_code,
        iataCode: null,
        latitude: place.location.coordinates.coordinates[1],
        longitude: place.location.coordinates.coordinates[0],
        name: place.location.name,
        timeZone: place.location.time_zone,
        updatedAt: place.location.updated_at["$date"],
      },
      relationships: {
        types: {
          data: types,
        }
      }
    }

    const addRequest = objectStore.add(transformed);
  }

  inject_places();
}

function count_places() {
  const transaction = db.transaction("places", "readonly");
  const objectStore = transaction.objectStore("places");
  const countRequest = objectStore.count();

  countRequest.onerror = (event) => {
    console.log(event);
  };

  countRequest.onsuccess = (event) => {
    if (countRequest.result != 0) {
      console.log("Places already indexed, skipping.");
      inject_places();
    } else {
      console.log("No places in DB, indexing...");
      show_loader("Indexing places, this could take several minutes...");

      if (staticPlacesFile != "") {
        load_static_places();
      } else {
        load_places();
      }
    }
  };
}

function inject_places() {
  const placesList = document.getElementById("places");
  const transaction = db.transaction("places", "readonly");
  const objectStore = transaction.objectStore("places");
  const openCursorRequest = objectStore.openCursor();
  let new_children = []


  openCursorRequest.onerror = (event) => {
    console.log(event);
  };

  openCursorRequest.onsuccess = (event) => {
    const cursor = event.target.result;

    if (!cursor) {
      placesList.replaceChildren(...new_children)
      hide_loader();
      return;
    }

    const option = document.createElement("option");
    option.value = cursor.value.id;
    option.innerText =
      cursor.value.attributes.name + ", " + cursor.value.attributes.countryCode;

    new_children.push(option);
    cursor.continue();

  };
}

function show_loader(status_message = "") {
  const container = document.getElementById("loader");
  container.classList.add("overlay");
  container.innerHTML =
    '<div><div class="lds-heart"><div></div></div><br><center>' +
    status_message +
    "</center></div>";
}

function hide_loader() {
  const container = document.getElementById("loader");
  container.classList.remove("overlay");
  container.innerHTML = "";
}

function flatten(resource, included) {
  if (!resource || !resource.hasOwnProperty("relationships")) {
    return resource;
  }

  for (const key of Object.keys(resource.relationships)) {
    if (resource.relationships[key].data instanceof Array) {
      for (const [i, value] of resource.relationships[key].data.entries()) {
        resource.relationships[key].data[i] = flatten(
          included[value.type + value.id],
          included
        );
      }
    } else {
      resource.relationships[key].data = flatten(
        included[
          resource.relationships[key].data.type +
            resource.relationships[key].data.id
        ],
        included
      );
    }
  }

  return resource;
}

function sort_legs(a, b) {
  a_date = new Date(a.attributes.departureAt);
  b_date = new Date(b.attributes.departureAt);
  a2_date = new Date(a.attributes.arrivalAt);
  b2_date = new Date(b.attributes.arrivalAt);

  if (a_date < b_date) {
    return -1;
  }

  if (a_date > b_date) {
    return 1;
  }

  if (a2_date < b2_date) {
    return -1;
  }

  if (a2_date > b2_date) {
    return 1;
  }

  return 0;
}

function sort_segments(a, b) {
  order = 0;
  leg_idx = 0;

  while (
    order == 0 &&
    leg_idx < a.relationships.legs.data.length &&
    leg_idx < b.relationships.legs.data.length
  ) {
    order = sort_legs(
      a.relationships.legs.data[leg_idx],
      b.relationships.legs.data[leg_idx]
    );
    leg_idx++;
  }

  return order;
}

function sort_trips(a, b) {
  order = 0;
  segment_idx = 0;

  while (
    order == 0 &&
    segment_idx < a.relationships.segments.data.length &&
    segment_idx < b.relationships.segments.data.length
  ) {
    order = sort_segments(
      a.relationships.segments.data[segment_idx],
      b.relationships.segments.data[segment_idx]
    );
    segment_idx++;
  }

  return order;
}

function nice_format_seconds(secs) {
  let hours = Math.floor(secs / 3600);
  let minutes = Math.floor((secs % 3600) / 60);
  let nice = "";

  if (hours > 0) {
    nice += hours + " hours ";
  }

  if (minutes > 0) {
    if (hours > 0) {
      nice += "and ";
    }

    nice += minutes + " minutes";
  }

  return nice.trim();
}

function getMsSinceMidnight(d) {
  var e = new Date(d);
  return d - e.setHours(0, 0, 0, 0);
}

function haversine_distance(coords1, coords2) {
  function toRad(x) {
    return (x * Math.PI) / 180;
  }

  var lon1 = coords1[0];
  var lat1 = coords1[1];

  var lon2 = coords2[0];
  var lat2 = coords2[1];

  var R = 6371 * 1000;

  var x1 = lat2 - lat1;
  var dLat = toRad(x1);
  var x2 = lon2 - lon1;
  var dLon = toRad(x2);
  var a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) *
      Math.cos(toRad(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  var d = R * c;

  return d;
}

function inject_trips(tripSearchId, response, origin, destination, searchOffers) {
  hide_loader();

  const showDebug = document.getElementById("show-debug").checked;
  const showMaps = document.getElementById("show-maps").checked;
  const container = document.getElementById("result");

  if (response.data.length == 0) {
    container.innerText = "No possible trips found.";
    return;
  }

  new_children = []

  let mega = document.createElement("h2");
  mega.innerText = "Search Results: " + response.data.length + " trips found";
  new_children.push(mega);

  let searchInfo = document.createElement("dl");
  searchInfo.className = "row";

  if (showDebug) {
    searchInfo.innerHTML +=
      '<dt class="col-sm-2">Trip Search ID</dt><dd class="col-sm-10">' +
      tripSearchId +
      "</dd>";
  }
  searchInfo.innerHTML +=
    '<dt class="col-sm-2">Session Token</dt><dd class="col-sm-10">' +
    sessionToken +
    "</dd>";
  if (showDebug) {
    searchInfo.innerHTML += '<dt class="col-sm-2">Provider Mapping</dt>';
  }
    let provider_mapping = document.createElement("dd");
    provider_mapping.className = "col-sm-10"
    if (showDebug) {
    searchInfo.append(provider_mapping);
  }
  new_children.push(searchInfo);
  if (showDebug) {
    inject_provider_mapping(origin, provider_mapping)
    inject_provider_mapping(destination, provider_mapping)
  }

  let included = {};

  for (const resource of response.included) {
    included[resource.type + resource.id] = resource;
  }

  let stats = {
    earliest: { trip_idx: [], time: Number.MAX_SAFE_INTEGER },
    fastest: { trip_idx: [], time: Number.MAX_SAFE_INTEGER },
    shortest: { trip_idx: [], time: Number.MAX_SAFE_INTEGER },
    environment: { trip_idx: [], time: Number.MAX_SAFE_INTEGER },
  };

  trips = [];

  for (const [i, resource] of response.data.entries()) {
    trip = flatten(resource, included);

    for (const [j, segment] of trip.relationships.segments.data.entries()) {
      segment.relationships.legs.data.sort(sort_legs);
      trip.relationships.segments.data[j] = segment;
    }

    trip.relationships.segments.data.sort(sort_segments);
    trips.push(trip);
  }

  trips.sort(sort_trips);

  for (let i = 0; i < trips.length; i++) {
    const trip = trips[i];
    firstSegment = trip.relationships.segments.data[0];
    lastSegment =
      trip.relationships.segments.data[
        trip.relationships.segments.data.length - 1
      ];
    departsAt = new Date(
      firstSegment.relationships.legs.data[0].attributes.departureAt
    );
    arrivesAt = new Date(
      lastSegment.relationships.legs.data[
        lastSegment.relationships.legs.data.length - 1
      ].attributes.arrivalAt
    );

    let total =
      Math.floor(arrivesAt.getTime() / 1000) -
      Math.floor(departsAt.getTime() / 1000);
    let totalDistance = 0;
    let totalEmission = 0;

    for (const segment of trip.relationships.segments.data) {
      for (const leg of segment.relationships.legs.data) {
        totalDistance += haversine_distance(
          [leg.attributes.origin.longitude, leg.attributes.origin.latitude],
          [
            leg.attributes.destination.longitude,
            leg.attributes.destination.latitude,
          ]
        );
      }
    }

    if (stats.earliest.time > arrivesAt.getTime()) {
      stats.earliest.trip_idx = [i];
      stats.earliest.time = arrivesAt.getTime();
    } else if (stats.earliest.time == arrivesAt.getTime()) {
      stats.earliest.trip_idx.push(i);
    }

    if (stats.fastest.time > total) {
      stats.fastest.trip_idx = [i];
      stats.fastest.time = total;
    } else if (stats.fastest.time == total) {
      stats.fastest.trip_idx.push(i);
    }

    if (stats.shortest.time > totalDistance) {
      stats.shortest.trip_idx = [i];
      stats.shortest.time = totalDistance;
    } else if (stats.shortest.time == totalDistance) {
      stats.shortest.trip_idx.push(i);
    }

    if (stats.environment.time > totalEmission) {
      stats.environment.trip_idx = [i];
      stats.environment.time = totalEmission;
    } else if (stats.environment.time == totalEmission) {
      stats.environment.trip_idx.push(i);
    }

    trip.totalTime = total;
    trip.totalDistance = totalDistance;
    trip.totalEmission = totalEmission;
    trip.direct = trip.relationships.segments.data.length == 1;
    trip.earliest = false;
    trip.fastest = false;
    trip.shortest = false;
    trip.environment = false;
    response.data[i] = trip;
  }

  for (const idx of stats.earliest.trip_idx) {
    response.data[idx].earliest = true;
  }

  for (const idx of stats.fastest.trip_idx) {
    response.data[idx].fastest = true;
  }

  for (const idx of stats.shortest.trip_idx) {
    response.data[idx].shortest = true;
  }

  for (const idx of stats.environment.trip_idx) {
    response.data[idx].environment = true;
  }

  for (const [i, trip] of response.data.entries()) {
    let header = document.createElement("h3");
    header.textContent = "Journey #" + (i + 1);
    let subtext = document.createElement("small");

    subtext.className = "text-muted";
    subtext.textContent = " - " + (trip.relationships.segments.data.length - 1);
    subtext.textContent +=
      " connection(s), " + nice_format_seconds(trip.totalTime);
    subtext.textContent +=
      ", " + Math.round((trip.totalDistance / 1000) * 10) / 10;
    subtext.textContent += "km";

    header.append(subtext);

    const infoList = document.createElement("dl");
    infoList.className = "row";

    if (showDebug) {
      infoList.innerHTML +=
        '<dt class="col-sm-2">Trip ID</dt><dd class="col-sm-10">' +
        trip.id +
        "</dd>";
    }

    if (searchOffers) {
      if (showDebug) {
        infoList.innerHTML +=
          '<dt class="col-sm-2">Offer Search ID</dt><dd class="col-sm-10" id="offer-search-' +
          trip.id +
          '"><div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div></dd>';
        infoList.innerHTML +=
          '<dt class="col-sm-2">Trace ID</dt><dd class="col-sm-10" id="trace-' +
          trip.id +
          '"><div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div></dd>';
      }

      infoList.innerHTML +=
        '<dt class="col-sm-2">Offers</dt><dd class="col-sm-10" id="offers-' +
        trip.id +
        '"><div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div></dd>';
      search_offers(trip.id, showDebug);
    }

    let badges = document.createElement("p");

    if (trip.direct) {
      let badge = document.createElement("span");
      badge.className = "badge bg-primary";
      badge.innerText = "Direct";
      badges.append(badge);

      badge = document.createElement("span");
      badge.innerText = " ";
      badges.append(badge);
    }

    if (trip.earliest) {
      let badge = document.createElement("span");
      badge.className = "badge bg-warning";
      badge.innerText = "Earliest Arrival";
      badges.append(badge);

      badge = document.createElement("span");
      badge.innerText = " ";
      badges.append(badge);
    }

    if (trip.fastest) {
      let badge = document.createElement("span");
      badge.className = "badge bg-info";
      badge.innerText = "Fastest Journey";
      badges.append(badge);

      badge = document.createElement("span");
      badge.innerText = " ";
      badges.append(badge);
    }

    if (trip.shortest) {
      let badge = document.createElement("span");
      badge.className = "badge bg-secondary";
      badge.innerText = "Shortest Distance";
      badges.append(badge);

      badge = document.createElement("span");
      badge.innerText = " ";
      badges.append(badge);
    }

    new_children.push(header);
    new_children.push(badges);
    new_children.push(infoList);

    let description = document.createElement("table");
    description.id = "description" + i;
    description.className = "table table-sm table-striped";

    let head = document.createElement("thead");
    let row = document.createElement("tr");
    let cell = document.createElement("th");
    cell.textContent = "#";
    row.append(cell);

    cell = document.createElement("th");
    cell.textContent = "Name";
    row.append(cell);

    cell = document.createElement("th");
    cell.textContent = "From";
    row.append(cell);

    cell = document.createElement("th");
    cell.textContent = "To";
    row.append(cell);

    cell = document.createElement("th");
    cell.textContent = "Departure";
    row.append(cell);

    cell = document.createElement("th");
    cell.textContent = "Arrival";
    row.append(cell);

    head.append(row);
    description.append(head);

    let body = document.createElement("tbody");
    let prev_date = "";

    trip.relationships.segments.data.forEach(function (segment, k) {
      let curr_date = new Date(
        segment.relationships.legs.data[0].attributes.departureAt
      ).toLocaleDateString(getLang(), {
        timeZone: segment.relationships.legs.data[0].attributes.origin.timeZone,
      });

      if (prev_date != curr_date) {
        let item = document.createElement("tr");
        let cell = document.createElement("td");
        cell.colSpan = 6;
        cell.innerHTML = "<small>" + curr_date + "</small>";
        cell.classList.add("text-center");
        item.append(cell);
        body.append(item);
      }

      prev_date = curr_date;

      let item = document.createElement("tr");

      if (k == 0) {
        item.className = "table-success";
      } else if (k == trip.relationships.segments.data.length - 1) {
        item.className = "table-danger";
      }

      let cell = document.createElement("td");
      cell.textContent = k + 1;
      item.append(cell);

      let icon = document.createElement("i");
      icon.className =
        "fas fa-" +
        icons[segment.relationships.legs.data[0].relationships.legType.data.id];
      let text = document.createElement("span");
      text.textContent = " " + segment.attributes.name;

      cell = document.createElement("td");
      cell.append(icon);
      cell.append(text);
      item.append(cell);

      cell = document.createElement("td");
      cell.textContent =
        segment.relationships.legs.data[0].attributes.origin.name;
      item.append(cell);

      cell = document.createElement("td");
      cell.textContent =
        segment.relationships.legs.data[
          segment.relationships.legs.data.length - 1
        ].attributes.destination.name;
      item.append(cell);

      cell = document.createElement("td");
      cell.textContent = new Date(
        segment.relationships.legs.data[0].attributes.departureAt
      ).toLocaleTimeString(getLang(), {
        timeZone: segment.relationships.legs.data[0].attributes.origin.timeZone,
      });
      item.append(cell);

      cell = document.createElement("td");
      cell.textContent = new Date(
        segment.relationships.legs.data[
          segment.relationships.legs.data.length - 1
        ].attributes.arrivalAt
      ).toLocaleTimeString(getLang(), {
        timeZone:
          segment.relationships.legs.data[
            segment.relationships.legs.data.length - 1
          ].attributes.destination.timeZone,
      });
      item.append(cell);

      body.append(item);
    });

    if (showMaps) {
      let map = document.createElement("div");
      map.id = "map" + i;
      map.className = "map col-sm";
      new_children.push(map);
    }

    description.append(body);
    new_children.push(description);
  }

  container.replaceChildren(...new_children)

  if (showMaps) {
    for (const [i, trip] of response.data.entries()) {
      render_map("map" + i, trip)
    }
  }
}

async function load_places() {
  let url = "/places?page[limit]=100";

  while (true) {
    const response = await fetch(url).then((res) => res.json())
    for (const place of response.data) {
      const transaction = db.transaction("places", "readwrite");
      const objectStore = transaction.objectStore("places");
      const addRequest = objectStore.add(place);
    }

    if (response.data.length == 0) {
      break
    }

    url = response.links.next
  }

  inject_places();
}

function inject_offers(response, offerSearchId, tripId, searchStatus, showDebug) {
  const status = document.getElementById("offers-" + tripId);
  if (response.data.length > 0) {
    status.innerHTML =
      '<i class="fas fa-check"></i> ' + response.data.length + " offer(s)";
    let pricesList = [];

    included = {};

    for (const resource of response.included) {
      included[resource.type + resource.id] = resource;
    }

    for (const item of response.data) {
      const offer = flatten(item, included);
      pricesList.push("<li>Offer " + offer.id + ":<ol>")
      for (const group of offer.relationships.groups.data) {
        pricesList.push("<li>")

        if (showDebug && group.meta && group.meta.providerId) {
          pricesList.push("Options from " + uuidToName[group.meta.providerId] + ":")
        } else if (group.meta && group.meta.providerId) {
          pricesList.push("Options " + Array.from(uuidToName[group.meta.providerId])[0].toUpperCase() + ":")
        } else {
          pricesList.push("Options:")
        }

        pricesList.push("<ul>")
        for (const option of group.relationships.options.data) {
          pricesList.push("<li>" + option.id + " (" + option.attributes.brandName + "): " + option.attributes.price.amount + " " + option.attributes.price.currency + "</li>")
        }
        pricesList.push("</ul></li>")
      }
      pricesList.push("</ol></li>")
    }

    status.innerHTML = "<ul style='font-size: 0.8em'>" + pricesList.join('') + "</ul>";

  } else {
    status.innerHTML =
      '<i class="fas fa-times-circle"></i> ' + response.data.length + " offer(s)";
  }
}

function load_offers(id, tripId, showDebug) {
  fetch("/offers/searches/" + id)
    .then((res) => res.json())
    .then((response) => {
      if (response.data.attributes.status == "completed") {
        fetch("/offers/searches/" + id + "/offers?include=groups,groups.options")
          .then((res) => res.json())
          .then((offersResponse) => {
            inject_offers(
              offersResponse,
              id,
              tripId,
              response.data.attributes.status,
              showDebug
            );
          });
      } else if (response.data.attributes.status == "failed") {
        const status = document.getElementById("offers-" + tripId);
        status.innerHTML = '<i class="fas fa-exclamation-circle"></i> System Failure';
      } else {
        setTimeout(() => {
          load_offers(id, tripId, showDebug);
        }, "5000");
      }
    }).catch(error => show_loader("An unexpected error has occurred. Please reload the application.<br>" + error));
}

function load_trips(id, origin, destination) {
  fetch("/trips/searches/" + id)
    .then((res) => res.json())
    .then((response) => {
      if (
        response.data.attributes.status == "completed" ||
        response.data.attributes.status == "failed"
      ) {
        fetch(
          "/trips/searches/" +
            id +
            "/trips?page[limit]=100&include=segments,segments.legs,segments.legs.legType"
        )
          .then((res) => res.json())
          .then((response) => {
            inject_trips(id, response, origin, destination, document.getElementById("search-offers").checked);
          }).catch(error => show_loader("An unexpected error has occurred. Please reload the application.<br>" + error));
      } else {
        setTimeout(() => {
          load_trips(id, origin, destination);
        }, "2000");
      }
    }).catch(error => show_loader("An unexpected error has occurred. Please reload the application.<br>" + error));
}

function search_offers(tripId, showDebug) {
  setTimeout(() => {
    fetch("/offers/searches", {
      method: "POST",
      headers: {
        "Content-Type": "application/vnd.api+json",
      },
      body: JSON.stringify({
        data: {
          type: "trip-offer-searches",
          attributes: {
            sessionToken: sessionToken,
            passengers: [
              {
                dateOfBirth: "1990-10-25",
              },
            ],
          },
          relationships: {
            trips: {
              data: [
                {
                  id: tripId,
                  type: "trips",
                },
              ],
            },
          },
        },
      }),
    })
      .then((response) => {
        const trace = document.getElementById("trace-" + tripId);

        if (trace) {
          trace.innerHTML = response.headers.get("x-request-id") || "<em>n/a</em>";
        }
        return response.json()
      })
      .then((data) => {

        const search = document.getElementById("offer-search-" + tripId);
        if (search) {
          search.innerHTML = data.data.id;
        }
        load_offers(data.data.id, tripId, showDebug);
      }).catch(error => show_loader("An unexpected error has occurred. Please reload the application.<br>" + error));
  }, Math.floor(Math.random() * 10000));
}

function clear_places_cache() {
  if (!window.confirm("Do you really want to remove all cached places?")) {
    return;
  }

  show_loader("Removing cached places, please wait...");

  const transaction = db.transaction("places", "readwrite");
  const objectStore = transaction.objectStore("places");
  const objectStoreRequest = objectStore.clear();

  transaction.oncomplete = (event) => {
    location.reload();
  };
}

function search_trips(event) {
  event.preventDefault();
  show_loader("Searching for trips, please wait...");

  const origin = document.getElementById("origin").value;
  const destination = document.getElementById("destination").value;
  const departureAt = document.getElementById("departure-at").value;
  const transaction = db.transaction("places", "readwrite");
  const objectStore = transaction.objectStore("places");
  const originRequest = objectStore.get(origin);
  const destinationRequest = objectStore.get(destination);
  const legTypes = document.querySelectorAll("input[name=leg-types]:checked")
  const useTripCandidates = document.getElementById("use-trip-candidates").checked;

  let allowedSegmentTypes = []

  legTypes.forEach(function(legType) {
    allowedSegmentTypes.push({
      id: legType.value,
      type: "leg-types",
    })
  })

  originRequest.onsuccess = (event) => {
    destinationRequest.onsuccess = (event) => {
      const originTimeZone = originRequest.result.attributes.timeZone;
      if (useTripCandidates) {
        let originCity = false
        let destinationCity = false

        for (const type of originRequest.result.relationships.types.data) {
          if (type.id == "city") {
            originCity = true
            break
          }
        }

        for (const type of destinationRequest.result.relationships.types.data) {
          if (type.id == "city") {
            destinationCity = true
            break
          }
        }

        fetch("/trip-candidates/searches", {
          method: "POST",
          headers: {
            "Content-Type": "application/vnd.api+json",
          },
          body: JSON.stringify({
            data: {
              type: "trip-candidate-searches",
              attributes: {
                sessionToken: sessionToken,
                criteria: [{
                  origin: {
                    latitude: originRequest.result.attributes.latitude,
                    longitude: originRequest.result.attributes.longitude,
                    precision: originCity ? "area" : "precise"
                  },
                  destination: {
                    latitude: destinationRequest.result.attributes.latitude,
                    longitude: destinationRequest.result.attributes.longitude,
                    precision: destinationCity ? "area" : "precise"
                  },
                  departureAfter: dayjs.tz(departureAt, originTimeZone).format(),
                }],
                passengers: [{
                  dateOfBirth: "1990-10-25"
                }],
              },

              relationships: {
                allowedSegmentTypes: {
                  data: allowedSegmentTypes,
                },
              },
            },
          }),
        })
        .then((response) => response.json())
        .then((data) => {
          load_trip_candidates(data.data.id, originRequest.result, destinationRequest.result);
        }).catch(error => show_loader("An unexpected error has occurred. Please reload the application.<br>" + error));
      } else {
        fetch("/trips/searches", {
          method: "POST",
          headers: {
            "Content-Type": "application/vnd.api+json",
          },
          body: JSON.stringify({
            data: {
              type: "trip-searches",
              attributes: {
                departureAfter: dayjs.tz(departureAt, originTimeZone).format(),
              },
              relationships: {
                origin: {
                  data: {
                    id: origin,
                    type: "places",
                  },
                },
                destination: {
                  data: {
                    id: destination,
                    type: "places",
                  },
                },
                allowedSegmentTypes: {
                  data: allowedSegmentTypes,
                },
              },
            },
          }),
        })
          .then((response) => response.json())
          .then((data) => {
            load_trips(data.data.id, originRequest.result, destinationRequest.result);
          }).catch(error => show_loader("An unexpected error has occurred. Please reload the application.<br>" + error));
      }
    }
  };
}


window.onload = () => {
  show_loader("Initializing UI, please wait...");
  const DBOpenRequest = window.indexedDB.open("places");

  DBOpenRequest.onupgradeneeded = (event) => {
    db = event.target.result;
    const objectStore = db.createObjectStore("places", { keyPath: "id" });

    console.log("Object store created.");
  };

  DBOpenRequest.onerror = (event) => {
    console.log(event);
  };

  DBOpenRequest.onsuccess = (event) => {
    db = DBOpenRequest.result;

    console.log("Database opened.");
    count_places();
  };

  const searchForm = document.getElementById("search-form");

  searchForm.addEventListener("submit", search_trips);
  document.getElementById("clear-places-cache").addEventListener("click", clear_places_cache);
};

window.onerror = function(msg, url, line, col, error) {
  show_loader("An unexpected error has occurred. Please reload the application.<br>" + error);
  return true;
};
