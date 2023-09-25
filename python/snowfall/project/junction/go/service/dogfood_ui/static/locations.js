function inject_provider_mapping(place, domElement) {
  let dl = document.createElement("dl");
  dl.className = "row";
  dl.innerHTML = "<dt class='col-sm-2'>"+place.attributes.name+"</dt>"
  domElement.append(dl)
  let dd = document.createElement("dd")
  dd.className = "col-sm-10"
  dl.append(dd)

  for (const type of place.relationships.types.data) {
    if (type.id == "city") {
      dd.innerHTML = "<em>Mapping lookup for cities is not implemented.</em>"
      return
    }
  }

  let innerDl = document.createElement("dl");
  innerDl.className = "row";

  dd.append(innerDl)

  fetch("/locations?id="+place.id, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      for (const [key, value] of Object.entries(data)) {
        let dt = document.createElement("dt");
        dt.innerText = key;
        dt.className = "col-sm-2"
        innerDl.append(dt)
        let dd = document.createElement("dd");
        dd.className = "col-sm-10"
        dd.innerText = value
        innerDl.append(dd)
      }
    }).catch(error => show_loader("An unexpected error has occurred. Please reload the application.<br>" + error));
}
