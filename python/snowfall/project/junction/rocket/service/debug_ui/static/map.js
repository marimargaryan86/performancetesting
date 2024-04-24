const type_colors = {
  SEGMENT_TYPE_FLIGHT: "red",
  SEGMENT_TYPE_TRAIN: "green",
  SEGMENT_TYPE_BUS: "yellow",
  SEGMENT_TYPE_FERRY: "orange",
  SEGMENT_TYPE_TAXI: "blue",
  SEGMENT_TYPE_CAR: "purple",
};

function render_map(element_id, route) {
  var mapItem = L.map(element_id);

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(mapItem);

  let latlngs = []
  let markers = [];
  let marker = L.marker(
    [
      route.segments[0].origin.latitude,
      route.segments[0].origin.longitude,
    ],
    { icon: greenIcon }
  )

  markers.push(marker);

  route.segments.forEach(function (segment, k) {
    let marker;

    if (k == route.segments.length - 1) {
      marker = L.marker(
        [
          segment.destination.latitude,
          segment.destination.longitude,
        ],
        { icon: redIcon }
      );
    } else {
      marker = L.marker([
        segment.destination.latitude,
        segment.destination.longitude,
      ]);
    }

    latlngs.push([
      segment.origin.latitude,
      segment.origin.longitude,
    ])
    latlngs.push([
      segment.destination.latitude,
      segment.destination.longitude,
    ])

    markers.push(marker);
    L.polyline([
      [
        segment.origin.latitude,
        segment.origin.longitude,
      ],
      [
        segment.destination.latitude,
        segment.destination.longitude,
      ]
    ], { color: type_colors[segment.segmentType] }).addTo(mapItem);
  })

  for (const marker of markers) {
    marker.addTo(mapItem);
  }

  mapItem.fitBounds(latlngs);
}
