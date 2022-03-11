<script>
	import MainMenu from '$lib/components/partials/main-menu.svelte';
</script>

<main>
	<MainMenu />

	<section class="work-space">
		<slot />
	</section>
</main>

<style>
	main {
		height: 100vh;
		display: grid;
		grid-template-columns: 240px 1fr;
	}

	.work-space {
		overflow: auto;
	}
</style>
