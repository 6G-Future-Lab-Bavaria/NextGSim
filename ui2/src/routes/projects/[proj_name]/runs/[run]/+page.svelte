<script lang="ts">
    import Test from "$lib/Test.svelte";
    import EventViewer from "$lib/EventViewer.svelte";
    import MetricsViewer from "$lib/MetricsViewer.svelte";
    import {onMount} from "svelte";
    import {loadRun, startRun} from "$lib/backend";

    export let data;
    let project = data.project;
    let run = data.run;

    let events = [];
    let metrics = [];

    let currTime = 0;

    onMount(async () => {
        await loadRun(project, run);
        let ws = new WebSocket(`ws://localhost:5000/projects/${project}/api/runs/${run}/ws`);
        ws.onmessage = (msg) => {
            let data = JSON.parse(msg.data);
            if (data.type == "EVENTS" && data.data.length > 0) {
                events.push(...data.data.map((ev) => {return {
                    time: ev.time,
                    comp: ev.component.name + "/" + ev.component.ref,
                    type: ev.type,
                    data: ev.data,
                }}));
                events = events;
            } else if (data.type == "METRICS") {
                metrics = data.data;
            } else if (data.type == "TIME") {
                currTime = data.data;
            }
        };
    });

    async function start() {
        await startRun(project, run);
    }

    let currentComp: string = "events";
</script>

<div id="app">
    <div id="header">
        <button on:click={() => currentComp = "topology"}>Topology</button>
        <button on:click={() => currentComp = "metrics"}>Metrics</button>
        <button on:click={() => currentComp = "events"}>Events</button>

        <button on:click={start}>Start</button>
        <span>{currTime}</span>
    </div>
    <div id="body">
        {#if currentComp === "events"}
            <EventViewer bind:events={events} />
        {:else if currentComp === "metrics" }
            <MetricsViewer bind:metrics={metrics} />
        {/if}
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
        flex: 1;
    }
</style>

<!--Test></Test-->