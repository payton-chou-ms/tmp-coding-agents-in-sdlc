<script lang="ts">
    import { onMount } from "svelte";

    interface Game {
        id: number;
        title: string;
        description: string;
        publisher: { id: number; name: string } | null;
        category: { id: number; name: string } | null;
        starRating: number | null;
    }

    interface FilterOption {
        id: number;
        name: string;
    }

    export let games: Game[] = [];
    let loading = true;
    let error: string | null = null;

    let categories: FilterOption[] = [];
    let publishers: FilterOption[] = [];
    let selectedCategoryId: string = '';
    let selectedPublisherId: string = '';

    const fetchFilterOptions = async () => {
        try {
            const [catResponse, pubResponse] = await Promise.all([
                fetch('/api/categories'),
                fetch('/api/publishers')
            ]);
            if (catResponse.ok) categories = await catResponse.json();
            if (pubResponse.ok) publishers = await pubResponse.json();
        } catch {
            // Filter options are non-critical; silently ignore errors
        }
    };

    const fetchGames = async () => {
        loading = true;
        error = null;
        try {
            const params = new URLSearchParams();
            if (selectedCategoryId) params.set('category_id', selectedCategoryId);
            if (selectedPublisherId) params.set('publisher_id', selectedPublisherId);

            const url = `/api/games${params.toString() ? '?' + params.toString() : ''}`;
            const response = await fetch(url);
            if(response.ok) {
                games = await response.json();
            } else {
                error = `Failed to fetch data: ${response.status} ${response.statusText}`;
            }
        } catch (err) {
            error = `Error: ${err instanceof Error ? err.message : String(err)}`;
        } finally {
            loading = false;
        }
    };

    const clearFilters = () => {
        selectedCategoryId = '';
        selectedPublisherId = '';
        fetchGames();
    };

    $: activeFilterCount = (selectedCategoryId ? 1 : 0) + (selectedPublisherId ? 1 : 0);

    onMount(() => {
        fetchFilterOptions();
        fetchGames();
    });
</script>

<div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
        <h2 class="text-2xl font-medium text-slate-100">Featured Games</h2>

        <!-- Filter controls -->
        <div class="flex flex-wrap gap-3 items-center" data-testid="filter-controls">
            <select
                bind:value={selectedCategoryId}
                on:change={fetchGames}
                class="bg-slate-800 border border-slate-600 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                data-testid="category-filter"
                aria-label="Filter by category"
            >
                <option value="">All Categories</option>
                {#each categories as category (category.id)}
                    <option value={String(category.id)}>{category.name}</option>
                {/each}
            </select>

            <select
                bind:value={selectedPublisherId}
                on:change={fetchGames}
                class="bg-slate-800 border border-slate-600 text-slate-200 text-sm rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                data-testid="publisher-filter"
                aria-label="Filter by publisher"
            >
                <option value="">All Publishers</option>
                {#each publishers as publisher (publisher.id)}
                    <option value={String(publisher.id)}>{publisher.name}</option>
                {/each}
            </select>

            {#if activeFilterCount > 0}
                <button
                    on:click={clearFilters}
                    class="text-sm px-3 py-2 rounded-lg bg-blue-600/20 text-blue-300 border border-blue-500/40 hover:bg-blue-600/40 transition-colors"
                    data-testid="clear-filters"
                    aria-label="Clear all filters"
                >
                    Clear filters
                    <span class="ml-1 bg-blue-500/40 text-blue-200 text-xs rounded-full px-1.5 py-0.5">{activeFilterCount}</span>
                </button>
            {/if}
        </div>
    </div>

    {#if loading}
        <!-- loading animation -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {#each Array(6) as _, i}
                <div class="bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50">
                    <div class="p-6">
                        <div class="animate-pulse">
                            <div class="h-6 bg-slate-700 rounded w-3/4 mb-3"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/2 mb-4"></div>
                            <div class="h-3 bg-slate-700 rounded w-full mb-3"></div>
                            <div class="h-3 bg-slate-700 rounded w-5/6 mb-4"></div>
                            <div class="h-2 bg-slate-700 rounded-full w-full mb-2"></div>
                            <div class="h-4 bg-slate-700 rounded w-1/4 mt-4"></div>
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    {:else if error}
        <!-- error display -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-red-400">{error}</p>
        </div>
    {:else if games.length === 0}
        <!-- no games found -->
        <div class="text-center py-12 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700">
            <p class="text-slate-300">
                {#if activeFilterCount > 0}
                    No games match the selected filters.
                {:else}
                    No games available at the moment.
                {/if}
            </p>
        </div>
    {:else}
        <!-- game list -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="games-grid">
            {#each games as game (game.id)}
                <a 
                    href={`/game/${game.id}`} 
                    class="group block bg-slate-800/60 backdrop-blur-sm rounded-xl overflow-hidden shadow-lg border border-slate-700/50 hover:border-blue-500/50 hover:shadow-blue-500/10 hover:shadow-xl transition-all duration-300 hover:translate-y-[-6px]"
                    data-testid="game-card"
                    data-game-id={game.id}
                    data-game-title={game.title}
                >
                    <div class="p-6 relative">
                        <div class="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <div class="relative z-10">
                            <h3 class="text-xl font-semibold text-slate-100 mb-2 group-hover:text-blue-400 transition-colors" data-testid="game-title">{game.title}</h3>
                            
                            {#if game.category || game.publisher}
                                <div class="flex gap-2 mb-3">
                                    {#if game.category}
                                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-blue-900/60 text-blue-300" data-testid="game-category">
                                            {game.category.name}
                                        </span>
                                    {/if}
                                    {#if game.publisher}
                                        <span class="text-xs font-medium px-2.5 py-0.5 rounded bg-purple-900/60 text-purple-300" data-testid="game-publisher">
                                            {game.publisher.name}
                                        </span>
                                    {/if}
                                </div>
                            {/if}
                            
                            <p class="text-slate-400 mb-4 text-sm line-clamp-2" data-testid="game-description">{game.description}</p>
                            
                            <div class="mt-4 text-sm text-blue-400 font-medium flex items-center">
                                <span>View details</span>
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1 transform transition-transform duration-300 group-hover:translate-x-2" viewBox="0 0 20 20" fill="currentColor">
                                    <path fill-rule="evenodd" d="M12.293 5.293a1 1 0 011.414 0l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                                </svg>
                            </div>
                        </div>
                    </div>
                </a>
            {/each}
        </div>
    {/if}
</div>
