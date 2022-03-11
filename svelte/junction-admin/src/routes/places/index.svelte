<script lang="ts">
	import PlaceSearch from '$lib/components/places/place-search.svelte';
	import dependencies from '$lib/dependencies';
	import type { SearchData } from '$lib/services/places/client';

	async function search(data: SearchData): Promise<void> {
		await dependencies.placeClient.getPlaces(data);
	}
</script>

<section class="places">
	<h1 class="main-header">Places</h1>

	<PlaceSearch on:search={(e) => search(e.detail)} />

	<div>Places goes here</div>
</section>

<style>
	.places {
		padding: 16px;
	}
</style>
