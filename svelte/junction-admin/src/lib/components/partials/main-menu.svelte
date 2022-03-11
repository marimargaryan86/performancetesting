<script lang="ts">
	import routeConfig from '$lib/route-config';
</script>

<section class="main-menu">
	<nav>
		<ol>
			<li>
				<a href={routeConfig.start}>Start</a>
			</li>
			<li>
				<a href={routeConfig.places}>Places</a>
			</li>
		</ol>
	</nav>
</section>

<style>
	.main-menu {
		background-color: var(--color-teal-darker);
		color: var(--color-white);
	}

	nav ol {
		padding: 8px 0;
	}

	nav a {
		display: block;
		padding: 8px 16px;
		color: var(--color-white);
		text-decoration: none;
	}

	nav a:hover {
		color: var(--color-teal-light);
	}
</style>
