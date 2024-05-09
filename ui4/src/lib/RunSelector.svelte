<script lang="ts">
    import {createRun, getRuns} from "./backend";
    import StatusIndicator from "./StatusIndicator.svelte";

    export let project: string;

    let runs: {run_id: string, started: string, stopped: string, status: string}[];

    async function load() {
        runs = await getRuns(project);
    }

    async function newRun() {
        await createRun(project);
        runs = await getRuns(project);
    }

    function printableDate(isoDate: string | null) {
        if (isoDate == null) return "N/A";
        return new Date(Date.parse(isoDate)).toLocaleString()
    }

</script>

<div id="container">
    <button on:click={newRun}>+</button>
    {#await load() then _}
    <div class="table">
        <div class="table-header">
            <div>Run ID</div>
            <div>Started</div>
            <div>Stopped</div>
            <div>Status</div>
        </div>

        {#each runs as run}
        <div class="table-row"><a href="/projects/{project}/runs/{run.run_id}" style="display: contents;">
            <div>{run.run_id}</div>
            <div>{printableDate(run.started)}</div>
            <div>{printableDate(run.stopped)}</div>
            <div><StatusIndicator status={run.status}></StatusIndicator></div>
        </a></div>
        {/each}
    </div>
    {/await}
</div>

<style>
    #container {
        padding: 1em;
        width: 100%;
        font-weight: bold;
    }

    button {
		display: block;
		background-color: transparent;
		border: none;
		cursor: pointer;
		color: teal;
        font-size: 1.3rem;
        font-weight: bold;
    }

    .table {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, auto));
        margin-top: .5em;
    }

    .table-header, .table-row {
        display: contents;
    }

    .table-header > * {
        margin-bottom: .5em;
    }

    .table-row a {
        text-decoration: none;
        color: rgb(120, 120, 120);
    }

    .table-row > a > div {
        display: flex;
        align-items: center;
        justify-content: left;
    }

    #runs li {
        list-style: none;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        padding: .3em;
    }

    #runs li:hover {
        background-color: #eaeaea;
    }

    #runs a {
        text-decoration: none;
        color: inherit;
        font-weight: bold;
        display: flex;
        align-items: center;
    }

</style>
