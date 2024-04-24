let db;

const icons = {
  SEGMENT_TYPE_FLIGHT: "plane",
  SEGMENT_TYPE_TRAIN: "train",
  SEGMENT_TYPE_BUS: "bus",
  SEGMENT_TYPE_FERRY: "ship",
  SEGMENT_TYPE_TAXI: "taxi",
  SEGMENT_TYPE_CAR: "car",
};

Handlebars.registerHelper('segment_type_icon', function (segment_type) {
  return "fas fa-"+icons[segment_type]
})

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

function clear_places() {
  const transaction = db.transaction("places", "readwrite");
  const objectStore = transaction.objectStore("places");
  const clearRequest = objectStore.clear();

  clearRequest.onerror = (event) => {
    console.log(event);
  };
}

function set_loader_message(status_message) {
  const container = document.getElementById("loader-message");
  container.innerHTML = status_message
}

function show_loader(status_message = "") {
  const container = document.getElementById("loader");
  container.classList.add("overlay");
  container.innerHTML =
    '<div><div class="lds-heart"><div></div></div><br><center id="loader-message">' +
    status_message +
    "</center></div>";
}

function hide_loader() {
  const container = document.getElementById("loader");
  container.classList.remove("overlay");
  container.innerHTML = "";
}

window.onload = () => {
  show_loader("Initializing UI, please wait...");
  const DBOpenRequest = window.indexedDB.open("places");

  DBOpenRequest.onupgradeneeded = (event) => {
    db = event.target.result;
    const objectStore = db.createObjectStore("places", { keyPath: "location.id" });
  };

  DBOpenRequest.onerror = (event) => {
    console.log(event);
  };

  DBOpenRequest.onsuccess = (event) => {
    db = DBOpenRequest.result;
    count_places();
  };

  const searchForm = document.getElementById("search-form");

  searchForm.addEventListener("submit", search_routes);
  document.getElementById("clear-places-cache").addEventListener("click", clear_places_cache);
};

window.onerror = function(msg, url, line, col, error) {
  show_loader("An unexpected error has occurred. Please reload the application.<br>" + error);
  return true;
};
