async function inject_routes(response) {
  const source = document.getElementById("route-template").innerHTML;
  const routesTemplate = Handlebars.compile(source, {strict: true});
  const container = document.getElementById("result");
  let htmlString = "";

  for (const idx in response.routes) {
    let origins = {}
    let destinations = {}

    for (const idx2 in response.routes[idx].segments) {
      origins[idx2] = await find_location(response.routes[idx].segments[idx2].origin.latitude, response.routes[idx].segments[idx2].origin.longitude)
      destinations[idx2] = await find_location(response.routes[idx].segments[idx2].destination.latitude, response.routes[idx].segments[idx2].destination.longitude)
    }

    htmlString += routesTemplate({mapId: "map"+idx, index: parseInt(idx) +1, origins: origins, destinations: destinations, route: response.routes[idx]})
  }

  container.innerHTML = htmlString

  for (idx in response.routes) {
    render_map("map"+idx, response.routes[idx])
  }

  hide_loader()
}

async function search_routes(event) {
  event.preventDefault();
  show_loader("Searching for routes, please wait...");

  const originId = document.getElementById("origin").value;
  const destinationId = document.getElementById("destination").value;
  const transaction = db.transaction("places", "readwrite");
  const objectStore = transaction.objectStore("places");
  const originRequest = objectStore.get(originId);
  const destinationRequest = objectStore.get(destinationId);
  const legTypes = document.querySelectorAll("input[name=leg-types]:checked")

  let allowedSegmentTypes = []

  legTypes.forEach(function(legType) {
    allowedSegmentTypes.push(legType.value)
  })

  const originPromise = new Promise(function (resolve, reject) {
    originRequest.onsuccess = (event) => {
      resolve(originRequest.result)
    };
  })
  const destinationPromise = new Promise(function (resolve, reject) {
    destinationRequest.onsuccess = (event) => {
      resolve(destinationRequest.result)
    };
  })

  await Promise.all([originPromise, destinationPromise])

  const origins = await load_locations(originRequest.result.mergedIds)
  const destinations = await load_locations(destinationRequest.result.mergedIds)

  let originCoordinates = []

  for (const origin of origins) {
    originCoordinates.push({
      latitude: origin.coordinates.latitude,
      longitude: origin.coordinates.longitude,
    })
  }

  let destinationCoordinates = []

  for (const destination of destinations) {
    destinationCoordinates.push({
      latitude: destination.coordinates.latitude,
      longitude: destination.coordinates.longitude,
    })
  }

  const response = await (await fetch("/routes", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      origins: originCoordinates,
      destinations: destinationCoordinates,
      allowedSegmentTypes: allowedSegmentTypes,
    }),
  })).json()

  inject_routes(response)
}
