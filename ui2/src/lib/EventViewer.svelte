<script lang="ts">
    import Timeline2 from "$lib/Timeline2.svelte";
    import {getEvents} from "$lib/backend";
    import Timeline from "$lib/Timeline.svelte";

    let events = [];
    let displayedEvents = [];
    let tracks: { [key: string] : {
            events: {time: number, comp: string, type: string}[]
        }} = {};

    $: {
        tracks = {};
        for (let ev of displayedEvents) {
            if (!tracks[ev.comp]) tracks[ev.comp] = {
                events: [],
            };
            tracks[ev.comp].events.push(ev);
        }
    }

    let comps = new Set<string>();
    let compIncludeStates = {};

    async function loadEvs() {
        events = await getEvents();
        for (let ev of events) {
            comps.add(ev.comp);
            compIncludeStates[ev.comp] = true;
        }
        displayedEvents = events;
    }

    $: {
        console.log(displayedEvents)}

    function click() {
        displayedEvents = events.filter((ev) => ev.comp == "EthernetInterface/n0.if0");
    }
    function click2() {
        displayedEvents = events.filter((ev) => ev.comp.startsWith("EthernetInterface"));
    }

    $: {
        let activeComps = Object.entries(compIncludeStates).filter((x) => x[1]).map((x) => x[0]);
        displayedEvents = events.filter((ev) => activeComps.includes(ev.comp));
    }

    function updateDisplayed() {
        let activeCompos = Object.entries(compIncludeStates).filter((x) => x[1]).map((x) => x[0]);
        console.log(activeCompos)
    }

</script>

{#await loadEvs() then _}
<div id="container">
    <div id="controls">
        <h4>Components</h4>
        <ul class="comp-ctrl">
            {#each comps as comp}
                <div>
                    <input type="checkbox" bind:checked={compIncludeStates[comp]} /> <label>{comp}</label>
                </div>
            {/each}
        </ul>
    </div>

    <div id="timeline">
        <Timeline2 tracks_={tracks}></Timeline2>
    </div>
</div>
{/await}

<style>
    #container {
        height: 100%;
        width: 100%;
        display: flex;
        flex-direction: row;
    }

    #controls {
        flex: 3;
        padding: 1em;
        position: relative;
    }

    #controls::after {
        content: "";
        position: absolute;
        width: 1px;
        background-color: black;
        right: 0;
        height: 100%;
        top: 0;
    }

    h4 {
        padding: 0;
    }

    .comp-ctrl {
        padding: 0;
        display: flex;
        flex-direction: column;
    }

    #timeline {
        flex: 12;
    }
</style>