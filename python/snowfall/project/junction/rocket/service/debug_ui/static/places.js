async function clear_places_cache() {
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

async function count_places() {
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
      load_places();
    }
  };
}

async function inject_places() {
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
    option.value = cursor.value.location.id;
    option.innerText =
      cursor.value.location.name + ", " + cursor.value.location.countryCode;

    new_children.push(option);
    cursor.continue();

  };
}

async function load_places(page_token = "", count = 0) {
  set_loader_message("Indexing places, this could take several minutes...<br>(" + count + " places indexed)");

  const response = await (await fetch("places?pageToken="+page_token, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      pageToken: page_token,
    }),
  })).json()

  for (const place of response.places) {
    if (!place.hasOwnProperty("mergedIds")) {
      continue
    }

    const transaction = db.transaction("places", "readwrite");
    const objectStore = transaction.objectStore("places");
    const addRequest = objectStore.add(place);
    count++
  }

  if (response.places.length > 0) {
    await load_places(response.nextPageToken, count);
  } else {
    await inject_places();
  }
}
