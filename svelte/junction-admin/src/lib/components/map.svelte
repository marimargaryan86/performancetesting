<script lang="ts">
  import type { CoordinatesModel } from "$lib/models/place";
  import type {
    Map,
    MapOptions,
    LeafletMouseEvent,
    Marker,
    MarkerOptions,
    IconOptions,
  } from "leaflet";
  import { createEventDispatcher, onMount } from "svelte";
  import "../../../node_modules/leaflet/dist/leaflet.css";

  export let center: CoordinatesModel = undefined;
  export let markers: { coordinates: CoordinatesModel }[] = [];
  let leafletMarkers: Marker[] = [];

  // eslint-disable-next-line
  let L: any;
  let container: HTMLDivElement;
  let clientWidth: number;
  let clientHeight: number;
  let map: Map;

  const dispatch = createEventDispatcher<{ selectPoint: CoordinatesModel }>();

  $: if (L && container) {
    map = L.map(container, {
      center: [50, 15],
      zoom: 3.5,
      minZoom: 1,
      maxBounds: [
        [90, 180],
        [-90, -180],
      ],
      doubleClickZoom: false,
    } as MapOptions);

    map.zoomControl.remove();
    map.addEventListener("click", (e: LeafletMouseEvent) =>
      dispatch("selectPoint", {
        latitude: parseFloat(e.latlng.lat.toFixed(4)),
        longitude: parseFloat(e.latlng.lng.toFixed(4)),
      }),
    );

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);
  }

  $: if (map) {
    leafletMarkers.forEach((marker) => marker.remove());
    leafletMarkers = markers.map((marker) => {
      const nextMarker: Marker = new L.marker(
        [marker.coordinates.latitude, marker.coordinates.longitude],
        {
          icon: L.icon({
            iconUrl: "/static/images/location.svg",
            iconAnchor: [15, 30],
            iconSize: [30, 30],
            className: "location-marker",
          } as IconOptions),
        } as MarkerOptions,
      );

      nextMarker.addTo(map);

      return nextMarker;
    });
  }

  $: if (map && center) {
    map.panTo([center.latitude, center.longitude], {
      animate: true,
    });
  }

  $: if (map) {
    clientWidth;
    clientHeight;

    map.invalidateSize();
  }

  onMount(async () => (L = (await import("leaflet")).default));
</script>

<div class="map" bind:this={container} bind:clientHeight bind:clientWidth />

<style>
  .map {
    display: inline-block;
    width: 400px;
    height: 280px;
    outline: 0;
  }

  .map :global(.leaflet-bottom.leaflet-right) {
    display: none;
  }

  .map :global(.location-marker) {
    filter: drop-shadow(1px 2px 2px rgba(5, 26, 44, 0.9));
  }
</style>
