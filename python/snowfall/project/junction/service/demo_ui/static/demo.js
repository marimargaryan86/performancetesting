dayjs.extend(window.dayjs_plugin_utc);
dayjs.extend(window.dayjs_plugin_timezone);

Handlebars.registerHelper('format_fares', function (trips) {
  return trips.map((trip) => trip.fare.marketingName).join(" + ");
})

Handlebars.registerHelper('format_money', function (money) {
  return new Intl.NumberFormat(navigator.language, { style: 'currency', currency: money.currencyCode }).format(money.units)
})

Handlebars.registerHelper('format_time', function (travelAt, departureDate) {
  const departureDateObject = dayjs(new Date(departureDate))
  const travelAtObject = dayjs(new Date(
    travelAt.year,
    travelAt.month-1,
    travelAt.day,
    travelAt.hours,
    travelAt.minutes,
  )).tz(travelAt.timeZone.id, true);

  formatted = travelAtObject.format('HH:mm')

  if (departureDateObject.date() != travelAtObject.date()) {
    formatted += " <sup>+" + travelAtObject.diff(departureDateObject, "day") + "</sup>"
  }

  return formatted
})

window.onload = () => {
  const searchForm = document.getElementById("search-form");
  const container = document.getElementById("result");
  const loader = document.getElementById("loader");
  const source = document.getElementById("journey-template").innerHTML;
  const journeyTemplate = Handlebars.compile(source, {strict: true});

  function inject_journeys(departureDate, journeys, providers) {
    providersMap = {}

    providers.forEach(function (provider, i) {
      providersMap[provider.id] = provider.name;
    })

    let htmlString = "";
    journeys.forEach(function (journey, i) {
      htmlString += journeyTemplate({journey: journey, departureDate: departureDate, providers: providersMap});
    });
    const dom = new DOMParser().parseFromString(htmlString, "text/html");
    container.append(dom.firstChild)
  }

  function fetch_providers(departureDate, task_id) {
    fetch("/providers", {
      method: "GET",
      headers: {
        "Accept": "application/json",
      },
    })
    .then((response) => {
      return response.json()
    })
    .then((body) => {
      fetch_trips(departureDate, task_id, body.providers)
    })
  }

  function fetch_trips(departureDate, task_id, providers) {
    fetch("/trips/"+task_id, {
      method: "GET",
      headers: {
        "Accept": "application/json",
      },
    })
    .then((response) => {
      return response.json()
    })
    .then((body) => {
      inject_journeys(departureDate, body.results, providers)

      if (!body.isInProgress) {
        loader.classList.add("invisible");
        return
      }

      setTimeout(() => {
        fetch_trips(departureDate, task_id, providers);
      }, "1000");
    });
  }

  function search_trips(event) {
    event.preventDefault();
    loader.classList.remove("invisible");
    container.innerText = ""

    const start = dayjs()
    const origin = document.getElementById("origin").value;
    const destination = document.getElementById("destination").value;
    const departureDate = dayjs(document.getElementById("departure-date").value);



    fetch("/trips", {
      method: "POST",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        passengers: [
          {
            type: "PASSENGER_TYPE_ADULT"
          }
        ],
        oneWay: {
          criterion: {
            origin: origin,
            destination: destination,
            departureDate: {
              year: departureDate.year(),
              month: departureDate.month() + 1,
              day: departureDate.date(),
            },
          },
        },
      }),
    })
    .then((response) => {
      return response.json()
    })
    .then((body) => {
      fetch_providers(departureDate, body.id)
    });
  }

  searchForm.addEventListener("submit", search_trips);
};
