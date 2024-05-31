<script lang="ts">
    import BinnedTimeseriesViewer from "./BinnedTimeseriesViewer.svelte";

    const COMPONENT_MAP: {[key: string]: ConstructorOfATypedSvelteComponent} = {
        "BinnedTimeseriesViewer": BinnedTimeseriesViewer
    };

    // todo: fix type change
    // todo: fix live updates (only updated when destroyed)

    export let metrics: {
        comp: string,
        name: string,
        ui_comp: string,
        data: any,
    }[];

    export let from_ts: number;
    export let to_ts: number;
    export let cursorPos_ts: number | null;
    export let selectedPos_ts: number;

</script>


<div id="controls">
</div>

<div id="metrics">
    {#each metrics as metric (metric.comp + metric.name) }
        <div class="metric">
            <div class="metric-id">{metric.comp}#{metric.name}</div>
            <div class="metric-container">
                {#if COMPONENT_MAP[metric.ui_comp] !== undefined}
                    <svelte:component
                            this={COMPONENT_MAP[metric.ui_comp]}
                            data={metric.data}
                            from_ts={from_ts}
                            to_ts={to_ts}
                            bind:cursorPos_ts={cursorPos_ts}
                            selectedPos_ts={selectedPos_ts}
                    ></svelte:component>
                {:else}
                    <p style="font-style: italic">Cannot render '{metric.ui_comp}'</p>
                {/if}
            </div>
        </div>
    {/each}
    {#if metrics.length === 0}
        <p style="font-style: italic">No metrics available</p>
    {/if}
</div>

<style>
    #controls {
        padding: 1em;
    }

    #metrics {
        min-height: 0;
        overflow-y: scroll;
    }

    .metric {
        margin-bottom: 1em;
        width: 100%;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: left;
    }

    .metric-id {
        margin-right: 1em;
        font-weight: bold;
    }

    .metric-container {
        width: 100%;
    }

    .metric-values {
        flex: auto;
        padding: 1em;
    }

    .metric-svg {
    }
</style>