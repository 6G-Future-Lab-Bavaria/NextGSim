<script lang="ts">
    import Test from "$lib/Test.svelte";
    import Timeline from "$lib/Timeline.svelte";
    import Timeline2 from "$lib/Timeline2.svelte";
    import {getEvents} from "$lib/backend.js";
    import EventViewer from "$lib/EventViewer.svelte";
    import MetricsViewer from "$lib/MetricsViewer.svelte";

    let currentComp = EventViewer;
</script>

<div id="app">
    <div id="header">
        <button on:click={() => currentComp = Test}>Network</button>
        <button on:click={() => currentComp = MetricsViewer}>Metrics</button>
        <button on:click={() => currentComp = EventViewer}>Events</button>
    </div>
    <div id="body">
        <svelte:component this={currentComp} />
    </div>
</div>

<style>
    :global(body) {
        font-family: sans-serif;
    }

    #app {
        display: flex;
        flex-direction: column;
        width: 100%;
        height: 100%;
    }

    #header {
        flex-basis: 2em;
        flex-grow: 0;
        flex-shrink: 0;
        border-bottom: 1px solid black;
        display: flex;
        flex-direction: row;
        align-items: baseline;
    }

    #header button {
        background-color: transparent;
        border: none;
        font-weight: bold;
        font-size: 1.2em;
        cursor: pointer;
        margin: 0 1em;
        margin-top: .1em;
    }

    #body {
        flex-basis: auto;
        flex-grow: 0;
        flex-shrink: 0;
    }
</style>

<!--Test></Test-->