<script lang="ts">

    import Tooltip from "./Tooltip.svelte";

    export let from_ts: number;
    export let to_ts: number;

    export let events: {
        comp: string,
        groups: {
            from_ts: number,
            to_ts: number,
            evs: {
                comp: string,
                data: any | null,
                time: number,
                type: string,
            }[],
        }[],
    }[] = [];

    // cursor pos in ts
    export let cursorPos_ts: number | null;

    $: range_ts = to_ts - from_ts;

    let tracksEl: HTMLDivElement;
    function mouseMoveTracks(ev: MouseEvent) {
        let trackX = tracksEl.getBoundingClientRect().x;
        let trackWidth = tracksEl.getBoundingClientRect().width;
        let x = ev.clientX - trackX;
        let relX = x / trackWidth;
        cursorPos_ts = relX * range_ts + from_ts;
    }

    function calcCursorPos_px(cursorPos_ts: number) {
        let trackWidth = tracksEl.getBoundingClientRect().width;
        return trackWidth * (cursorPos_ts - from_ts) / range_ts;
    }

    let comps: string[] = [];
    $: comps = events.map(el => el.comp);

    let compIncludeStates: {[key: string]: boolean} = {};
    for (let comp of comps) {
        compIncludeStates[comp] = true;
    }
    compIncludeStates = compIncludeStates;

    $: {
        comps;
        // set new without overriding existing settings
        for (let comp of comps) {
            if (compIncludeStates[comp] == undefined)
                compIncludeStates[comp] = true;
        }
        compIncludeStates = compIncludeStates;
    }

    let tooltipPos: [number, number] = [0,0];
    let tooltipVisible = false;
    let tooltipEvents = 0;
    let tooltipTypes: string[] = [];
    let tooltipFrom_ts = 0;
    let tooltipTo_ts = 1;
</script>

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

    <div id="tracks"
         bind:this={tracksEl}
        on:mousemove={mouseMoveTracks}
         on:mouseleave={() => cursorPos_ts = null}
    >
        {#if tracksEl !== undefined && cursorPos_ts !== null}
            <div id="cursor" style:left="{calcCursorPos_px(cursorPos_ts)}px"></div>
        {/if}
        {#each events as compEvs}
            {#if compIncludeStates[compEvs.comp]}
            <h5>{compEvs.comp}</h5>
            <div class="timeline">
                {#each compEvs.groups as group}
                    <div class="marker"
                         style:left="{100 * Math.min(1., (group.from_ts - from_ts) / range_ts)}%"
                         style:width="{100 * Math.min(1., (group.to_ts - group.from_ts) / range_ts)}%"
                        on:mouseover={(ev) => {
                            tooltipVisible = true;
                            tooltipPos = [ev.clientX, ev.clientY];
                            tooltipEvents = group.evs.length;
                            tooltipTypes = [...new Set(group.evs.map(e => e.type))].toSorted();
                            tooltipFrom_ts = group.from_ts;
                            tooltipTo_ts = group.to_ts;
                            // @ts-ignore
                            ev.target.style.backgroundColor = "teal";
                        }}
                         on:mouseleave={(ev) => {
                            tooltipVisible = false;
                            // @ts-ignore
                            ev.target.style.backgroundColor = "black";
                        }}
                    >
                    </div>
                {/each}
            </div>
            {/if}
        {/each}
    </div>

    <Tooltip pos={tooltipPos} visible={tooltipVisible}>
        <div id="tt-content">
            <p>{tooltipEvents} Event{tooltipEvents === 1 ? "" : "s"}</p>
            <p>Type(s): <span style="font-style: italic">{tooltipTypes.join(", ")}</span></p>
            {#if tooltipFrom_ts !== tooltipTo_ts}
            <p>{tooltipFrom_ts.toFixed(2)} - {tooltipTo_ts.toFixed(2)}</p>
            {:else}
            <p>{tooltipFrom_ts.toFixed(2)}</p>
            {/if}
        </div>
    </Tooltip>
</div>

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

    #tracks {
        flex: 12;
        display: flex;
        flex-direction: column;
        overflow-y: scroll;
        overflow-x: hidden;
        position: relative;
    }

    #cursor {
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        border-left: 2px solid black;
        z-index: -100;
        opacity: .3;
        pointer-events: none;
    }

    .timeline {
        position: relative;
        width: 100%;
        height: 2em;
        flex-grow: 0;
        flex-shrink: 0;
        background-color: lightgray;
    }

    .marker {
        position: absolute;
        left: 0;
        top: 4px;
        bottom: 4px;
        border-radius: 5px;
        background-color: black;
        min-width: 4px;
    }

    .marker::after {
        position: absolute;
        left: 0;
        top: 0;
        content: "";
        width: 10px;
        height: 100%;
        transform: translateX(-50%);
    }

    .marker.hover {
        background-color: teal;
    }

    #tt-content {
        background-color: lightgray;
        border-radius: .5em;
        padding: .5em;
    }

    #tt-content p {
        margin-top: .1em;
        margin-bottom: .1em;
    }
</style>