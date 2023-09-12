function render_map(element_id, trip) {
  var mapItem = L.map(element_id);

  L.tileLayer(
    "https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}",
    {
      attribution:
        'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: 18,
      id: "mapbox/streets-v11",
      tileSize: 512,
      zoomOffset: -1,
      accessToken:
        "pk.eyJ1IjoianlnZ2VuIiwiYSI6ImNrdDZmaGVsbDBodDMyd283dG9ucjdmejQifQ.4JXvYcrRq1FmBj3LqW5zDg",
    }
  ).addTo(mapItem);

  let latlngs = [];
  let markers = [];
  let marker = L.marker(
    [
      trip.relationships.segments.data[0].relationships.legs.data[0]
        .attributes.origin.latitude,
      trip.relationships.segments.data[0].relationships.legs.data[0]
        .attributes.origin.longitude,
    ],
    { icon: greenIcon }
  )

  markers.push(marker);
  latlngs.push(marker.getLatLng());

  trip.relationships.segments.data.forEach(function (segment, k) {
    let marker;

    if (k == trip.relationships.segments.data.length - 1) {
      marker = L.marker(
        [
          segment.relationships.legs.data[
            segment.relationships.legs.data.length - 1
          ].attributes.destination.latitude,
          segment.relationships.legs.data[
            segment.relationships.legs.data.length - 1
          ].attributes.destination.longitude,
        ],
        { icon: redIcon }
      );
    } else {
      marker = L.marker([
        segment.relationships.legs.data[
          segment.relationships.legs.data.length - 1
        ].attributes.destination.latitude,
        segment.relationships.legs.data[
          segment.relationships.legs.data.length - 1
        ].attributes.destination.longitude,
      ]);
    }

    markers.push(marker);

    segment.relationships.legs.data.forEach(function (leg, k) {
      if (k != segment.relationships.legs.data.length - 1) {
        latlngs.push([
          leg.attributes.destination.latitude,
          leg.attributes.destination.longitude,
        ]);
      }
    });

    latlngs.push(marker.getLatLng());
  })

  for (const marker of markers) {
    marker.addTo(mapItem);
  }

  let polyline = L.polyline(latlngs, { color: "blue" }).addTo(mapItem);
  mapItem.fitBounds(polyline.getBounds());
}
