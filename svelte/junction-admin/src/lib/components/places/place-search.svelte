<script lang="ts">
	import type { CoordinatesModel } from '$lib/models/common';
	import type { SearchData } from '$lib/services/places/client';
	import { createEventDispatcher } from 'svelte';
	import CoordinatesInput from '../ui/coordinates-input.svelte';

	let name: string | undefined = undefined;
	let coordinates: CoordinatesModel | undefined = undefined;
	let proximity = 0;

	$: name = name?.trim().length === 0 ? undefined : name;

	const dispatch = createEventDispatcher<{ search: SearchData }>();

	function search() {
		dispatch('search', { name, coordinates, proximity });
	}
</script>

<form class="place-search" on:submit|preventDefault={search}>
	<label>
		<span>Name</span>
		<input type="text" bind:value={name} />
	</label>

	<label for="coordinates">
		<span>Coordinates</span>
		<CoordinatesInput bind:value={coordinates} id="coordinates" />
	</label>

	<label>
		<span>Proximity ({proximity ?? 0}m)</span>
		<input type="range" min={0} max={1000} bind:value={proximity} class="raw" />
	</label>

	<button>Search</button>
</form>

<style>
	.place-search {
		display: inline-flex;
		background-color: var(--color-gray-light);
		padding: 16px;
	}

	label {
		display: inline-block;
		min-width: 300px;
	}

	label:not(:first-child) {
		margin-left: 4px;
	}

	label > span {
		display: block;
		font-size: 12px;
		margin-bottom: 4px;
	}

	label > input,
	label > :global(.coordinates-input) {
		width: 100%;
	}

	label > input[type='range'] {
		margin-top: 12px;
	}

	button {
		margin-left: 4px;
		align-self: flex-end;
	}
</style>
