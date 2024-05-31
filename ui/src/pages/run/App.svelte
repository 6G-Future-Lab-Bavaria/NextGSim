<script context="module" lang="ts">
	declare var project: string;
	declare var run: string;
</script>

<script lang="ts">

    import MetricsViewer from "../../lib/MetricsViewer.svelte";
    import EventViewer from "../../lib/EventViewer.svelte";
    import {onMount} from "svelte";
    import {
        getEvents,
        getMetrics,
        getRun,
        getRunConfig,
        getTopologyAtTime,
        stopRun
    } from "../../lib/backend";
    import StatusIndicator from "../../lib/StatusIndicator.svelte";
    import TimeSlider from "../../TimeSlider.svelte";
    import {FontAwesomeIcon} from "@fortawesome/svelte-fontawesome";
    import {faChartSimple, faDiagramProject, faExclamation, faFile} from "@fortawesome/free-solid-svg-icons";
    import {JSONEditor} from "svelte-jsoneditor";
    import TopologyViewer from "../../lib/TopologyViewer.svelte";

    let activePane = "c";

    const BIN_COUNT = 500;

    $: runStatus = "UNKNOWN";

    let currTimeWindow_ts = [0, 1];
    let selectedPos_ts: number = 0;

    $: currRange = currTimeWindow_ts[1] - currTimeWindow_ts[0];

    let minTime_ts = 0;
    let maxTime_ts = 1;

    let trackLive = true;

    function onTimeWindowChanged(ev: CustomEvent<{minTs:number, maxTs:number}>) {
        console.log(ev.detail.minTs, ev.detail.maxTs);
        currTimeWindow_ts = [ev.detail.minTs, ev.detail.maxTs];

        if (selectedPos_ts < ev.detail.minTs)
            selectedPos_ts = ev.detail.minTs;

        if (selectedPos_ts > ev.detail.maxTs)
            selectedPos_ts = ev.detail.maxTs;
    }

    async function setupWebsocket() {
        console.log("WS");
        let ws = new WebSocket(`ws://${window.location.host}/api/projects/${project}/runs/${run}/ws`);
        ws.onmessage = (msg) => {
            let data = JSON.parse(msg.data);
            if (data.type == "TIME") {
                maxTime_ts = data.data;
            } else if (data.type == "END") {
                maxTime_ts = data.data;
                runStatus = "STOPPED";
            }
        };
    }

    async function stop() {
        await stopRun(project, run);
    }

    let metrics: any[] | undefined = undefined;
    $: getMetrics(project, run, currTimeWindow_ts[0], currTimeWindow_ts[1], { "bin_count": BIN_COUNT })
            .then((m) => metrics = m);

    onMount(async () => {
        let runData = await getRun(project, run);
        runStatus = runData.status;
        maxTime_ts = runData.duration_ts;

        await setupWebsocket();
    });

    let cursorPos_ts: number | null = 0;

</script>

<div id="app">
    <header>
        <h1><a href="/projects/{project}">{project}</a> // {run}</h1>
        <div class="right">
            {#if runStatus === "RUNNING"}
            <button id="stop-btn" on:click={stop}>Stop</button>
            {/if}
            <StatusIndicator status={runStatus}></StatusIndicator>
        </div>
    </header>

    <main>
        <div id="time-slider">
            <TimeSlider bind:cursorPos_ts={cursorPos_ts} bind:selectedPos_ts={selectedPos_ts} trackLive={trackLive} absoluteMinTs={minTime_ts} absoluteMaxTs={maxTime_ts} on:onChange={onTimeWindowChanged} isLive={runStatus === "RUNNING"}></TimeSlider>
        </div>
        <div id="bottom">
            <aside>
                <ul id="sidebar-controls">
                    <li>
                        <button class:active={activePane==="c"}
                                on:click={() => activePane = "c"}
                        >
                            <FontAwesomeIcon icon={faFile}
                            fixedWidth={false}
                            size="1x"></FontAwesomeIcon>
                        </button>
                    </li>
                    <li>
                        <button class:active={activePane==="m"}
                                on:click={() => activePane = "m"}
                        ><FontAwesomeIcon icon={faChartSimple}
                        fixedWidth={false}
                        size="1x"></FontAwesomeIcon>
                        </button>
                    </li>
                    <li>
                        <button class:active={activePane==="t"}
                                on:click={() => activePane = "t"}
                        >
                            <FontAwesomeIcon icon={faDiagramProject}
                            fixedWidth={false}
                            size="1x"></FontAwesomeIcon>
                        </button>
                    </li>
                    <li>
                        <button class:active={activePane==="e"}
                                on:click={() => activePane = "e"}
                        >
                            <FontAwesomeIcon icon={faExclamation}
                            fixedWidth={false}
                            size="1x"></FontAwesomeIcon>
                        </button>
                    </li>
                </ul>
            </aside>
            <div id="main-pane">
                {#if activePane === "m" && metrics !== undefined}
                    <MetricsViewer bind:cursorPos_ts={cursorPos_ts} selectedPos_ts={selectedPos_ts} from_ts={currTimeWindow_ts[0]} to_ts={currTimeWindow_ts[1]} metrics={metrics}></MetricsViewer>
                {:else if activePane === "t"}
                    {#await getTopologyAtTime(project, run, selectedPos_ts, {}) then top}
                        <TopologyViewer topology={top}></TopologyViewer>
                    {/await}
                {:else if activePane === "e"}
                    {#await getEvents(project, run, currTimeWindow_ts[0], currTimeWindow_ts[1], { "min_ts_between": 0.01 * currRange }) then events}
                        <EventViewer bind:cursorPos_ts={cursorPos_ts} selectedPos_ts={selectedPos_ts} from_ts={currTimeWindow_ts[0]} to_ts={currTimeWindow_ts[1]} events={events}></EventViewer>
                    {/await}
                {:else if activePane === "c"}
                    {#await getRunConfig(project, run) then config}
                        <JSONEditor content={{json: config}} readOnly={true}></JSONEditor>
                    {/await}
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
        font-size: 1.4rem;
        flex: 1em;
        flex-grow: 0;
        border-bottom: 2px solid teal;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
    }

    header h1 {
        font-size: inherit;
        margin: .5em;
    }

    header .right {
        display: flex;
        align-items: center;
    }

    header a {
        text-decoration: none;
        color: inherit;
    }

    #stop-btn {
        /*width: 1em;
        height: 1em;*/
        margin: .5em;
        background-color: transparent;
        border: none;
        font-size: 1.5rem;
        font-weight: bold;
        cursor: pointer;
    }

    main {
        flex: auto;
        display: flex;
        flex-direction: column;
        min-height: 0;
    }

    #time-slider {
    }

    #bottom {
        flex: auto;
        display: flex;
        flex-direction: row;
        min-height: 0;
    }

    #main-pane {
        padding: 1em;
        box-sizing: border-box;
        width: 100%;
        min-height: 0;
        display: flex;
        flex-direction: column;
    }

    aside {
        border-right: 2px solid teal;
    }

    #sidebar-controls {
        padding: 0;
        display: flex;
        flex-direction: column;
        align-items: center;
        list-style: none;
    }

    #sidebar-controls li {
        text-decoration: none;
        margin: .5em;
    }

    #sidebar-controls li button {
        height: 2em;
        width: 2em;
        background-color: transparent;
        border: none;
        cursor: pointer;
        font-size: 1em;
        color: teal;
        padding: .4em;
        border-radius: 20%;
    }

    #sidebar-controls li button.active {
        font-weight: bold;
        background-color: #ebeaea;
    }

    main h4 {
        font-size: 1rem;
        margin: .7em;
    }


</style>

