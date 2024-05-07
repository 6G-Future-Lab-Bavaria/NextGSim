<script context="module" lang="ts">
	declare var project: string;
	declare var run: string;
</script>

<script lang="ts">

    import MetricsViewer from "../../lib/MetricsViewer.svelte";
    import EventViewer from "../../lib/EventViewer.svelte";
    import Test from "../../lib/Test.svelte";
    import {onMount} from "svelte";
    import {loadRun} from "../../lib/backend";

    let activePane = "m";

    let events = [];
    let metrics = [];
    let topology;

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
            } else if (data.type == "TOPOLOGY") {
                topology = data.data;
                console.log(topology)
            }
        };
    });

</script>

<div id="app">
    <header>
        <h1>{project} // {run}</h1>
    </header>

    <main>
        <div id="time-slider">TIME SLIDER</div>
        <div id="bottom">
            <aside>
                <ul>
                    <li>
                        <button class:active={activePane==="m"}
                                on:click={() => activePane = "m"}
                        >M</button>
                    </li>
                    <li>
                        <button class:active={activePane==="t"}
                                on:click={() => activePane = "t"}
                        >N</button>
                    </li>
                    <li>
                        <button class:active={activePane==="e"}
                                on:click={() => activePane = "e"}
                        >E</button>
                    </li>
                </ul>
            </aside>
            <div id="main-pane">
                {#if activePane === "m"}
                    <MetricsViewer metrics={metrics}></MetricsViewer>
                {:else if activePane === "t"}
                    <Test topology={topology}></Test>
                {:else if activePane === "e"}
                    <EventViewer events={events}></EventViewer>
                {/if}
            </div>
        </div>
    </main>

</div>

<style>

    :global(body) {
        height: 100%;
        width: 100%;
        margin: 0;
        font-family: sans-serif;
    }

    #app {
        width: 100vw;
        height: 100vh;
        display: flex;
        flex-direction: column;
        color: teal;
    }

    header {
        flex: 1em;
        flex-grow: 0;
        border-bottom: 2px solid teal;
    }

    header h1 {
        font-size: 1rem;
        margin: .5em;
    }

    main {
        flex: auto;
        display: flex;
        flex-direction: column;
    }

    #time-slider {
        background-color: lightgray;
        text-align: center;
        color: white;
        height: 4em;
    }

    #bottom {
        display: flex;
        flex-direction: row;
        height: 100%;
    }

    #main-pane {
        padding: 1em;
        box-sizing: border-box;
        width: 100%;
        height: 100%;
    }

    aside {
        border-right: 2px solid teal;
    }

    aside ul {
        padding: 0;
    }

    aside ul li {
        text-decoration: none;
        margin: .5em;
    }

    aside ul li button {
        background-color: transparent;
        border: none;
        cursor: pointer;
        font-size: 1em;
        color: teal;
        padding: .4em;
    }

    aside ul li button.active {
        font-weight: bold;
    }

    main h4 {
        font-size: 1rem;
        margin: .7em;
    }

    #pane-left, #pane-right {
        display: flex;
        flex-direction: column;
    }

    #pane-left {
        flex: 3;
    }

    #pane-right {
        flex: 1;
        margin-left: 1em;
    }


</style>

