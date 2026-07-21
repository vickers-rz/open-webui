<script lang="ts">
	export let items: any[] = [];
	export let rowHeight = 48;
	export let height = 384;
	export let overscan = 4;

	let scrollTop = 0;

	$: start = Math.max(0, Math.floor(scrollTop / rowHeight) - overscan);
	$: visibleCount = Math.ceil(height / rowHeight) + overscan * 2;
	$: end = Math.min(items.length, start + visibleCount);
	$: visibleItems = items.slice(start, end);
</script>

<div
	class="w-full overflow-y-auto"
	style:height="{height}px"
	on:scroll={(event) => {
		scrollTop = event.currentTarget.scrollTop;
	}}
>
	<div class="relative w-full" style:height="{items.length * rowHeight}px">
		{#each visibleItems as item, index (start + index)}
			<div
				class="absolute inset-x-0"
				style:top="{(start + index) * rowHeight}px"
				style:height="{rowHeight}px"
			>
				<slot {item} index={start + index} />
			</div>
		{/each}
	</div>
</div>
