<script lang="ts">
	import type { CoordinatesModel } from '$lib/models/common';

	export let value: CoordinatesModel = undefined;
	export let id: string | undefined = undefined;

	let latitude: number | undefined = value?.latitude;
	let longitude: number | undefined = value?.longitude;

	$: latitude = latitude ? Math.max(Math.min(latitude, 90), -90) : latitude;
	$: longitude = longitude ? Math.max(Math.min(longitude, 180), -180) : longitude;
	$: {
		if (!!latitude && latitude !== 0 && !!longitude && longitude !== 0) {
			value = { latitude, longitude };
		} else {
			value = undefined;
		}
	}
</script>

<div class="coordinates-input">
	<input
		type="number"
		bind:value={latitude}
		placeholder="Lat"
		min={-90}
		max={90}
		{id}
		step="any"
	/>
	<input
		type="number"
		bind:value={longitude}
		placeholder="Long"
		min={-180}
		max={180}
		step="any"
	/>
</div>

<style>
	.coordinates-input {
		display: inline-flex;
	}

	input {
		width: 50%;
	}

	input:not(:first-child) {
		margin-left: 4px;
	}
</style>
