<script lang="ts">
	import { onMount } from 'svelte';
	import { getTodayGames, searchPlayers, getStatCategories, type Game, type StatCategory } from '$lib/api';

	let games: Game[] = [];
	let categories: StatCategory[] = [];
	let loading = true;
	let searchQuery = '';
	let searchResults: any[] = [];
	let searching = false;
	let error = '';

	onMount(async () => {
		try {
			const [gamesData, categoriesData] = await Promise.all([
				getTodayGames(),
				getStatCategories()
			]);
			games = gamesData;
			categories = categoriesData;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Failed to load data';
			console.error('Error loading initial data:', err);
		} finally {
			loading = false;
		}
	});

	async function handleSearch() {
		if (searchQuery.length < 2) {
			searchResults = [];
			return;
		}

		searching = true;
		try {
			searchResults = await searchPlayers(searchQuery);
		} catch (err) {
			console.error('Search error:', err);
		} finally {
			searching = false;
		}
	}

	let searchTimeout: ReturnType<typeof setTimeout>;
	function onSearchInput() {
		clearTimeout(searchTimeout);
		searchTimeout = setTimeout(handleSearch, 300);
	}
</script>

<svelte:head>
	<title>NBA Stats Tracker - Home</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Header -->
	<header class="bg-white shadow-md">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
			<h1 class="text-3xl font-bold text-gray-900">NBA Stats Tracker</h1>
			<p class="text-gray-600 mt-1">PropsMadness-style player performance tracking</p>
		</div>
	</header>

	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<!-- Search Bar -->
		<div class="mb-8">
			<div class="relative">
				<input
					type="text"
					bind:value={searchQuery}
					on:input={onSearchInput}
					placeholder="Search players or teams..."
					class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				/>
				{#if searching}
					<div class="absolute right-3 top-3">
						<div class="animate-spin h-6 w-6 border-2 border-blue-500 rounded-full border-t-transparent"></div>
					</div>
				{/if}
			</div>

			<!-- Search Results -->
			{#if searchResults.length > 0}
				<div class="mt-2 bg-white rounded-lg shadow-lg border border-gray-200">
					{#each searchResults as player}
						<a
							href="/player/{player.slug}?stat=points"
							class="block px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
						>
							<div class="flex items-center justify-between">
								<div>
									<div class="font-semibold text-gray-900">{player.name}</div>
									<div class="text-sm text-gray-500">
										{player.position || 'N/A'} • {player.team || 'Free Agent'}
									</div>
								</div>
								<svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
									<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
								</svg>
							</div>
						</a>
					{/each}
				</div>
			{/if}
		</div>

		{#if error}
			<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-8">
				{error}
			</div>
		{/if}

		{#if loading}
			<div class="flex justify-center items-center py-12">
				<div class="animate-spin h-12 w-12 border-4 border-blue-500 rounded-full border-t-transparent"></div>
			</div>
		{:else}
			<!-- Today's Games -->
			<section class="mb-8">
				<h2 class="text-2xl font-bold text-gray-900 mb-4">Today's Games</h2>

				{#if games.length === 0}
					<div class="bg-white rounded-lg shadow p-8 text-center text-gray-500">
						No games scheduled for today.
					</div>
				{:else}
					<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
						{#each games as game}
							<div class="bg-white rounded-lg shadow-md hover:shadow-lg transition p-6">
								<div class="text-center">
									<div class="text-2xl font-bold text-gray-900 mb-2">
										{game.away_team} @ {game.home_team}
									</div>
									<div class="text-sm text-gray-600 mb-4">{game.start_time}</div>
									<div class="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded inline-block">
										{game.status}
									</div>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</section>

			<!-- Stat Categories Info -->
			<section>
				<h2 class="text-2xl font-bold text-gray-900 mb-4">Available Stats</h2>
				<div class="bg-white rounded-lg shadow-md p-6">
					<div class="flex flex-wrap gap-2">
						{#each categories as category}
							<span class="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
								{category.name}
							</span>
						{/each}
					</div>
				</div>
			</section>

			<!-- Quick Start Instructions -->
			<section class="mt-8">
				<div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
					<h3 class="text-lg font-semibold text-blue-900 mb-2">Getting Started</h3>
					<ol class="list-decimal list-inside text-blue-800 space-y-1">
						<li>Search for a player using the search bar above</li>
						<li>Click on a player to view their performance chart</li>
						<li>Adjust the draggable line to see hit rates</li>
						<li>Apply filters to analyze specific scenarios (H2H, Home/Away, etc.)</li>
					</ol>
				</div>
			</section>
		{/if}
	</div>
</div>
