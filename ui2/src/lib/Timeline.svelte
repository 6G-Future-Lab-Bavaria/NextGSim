<script lang="ts">
    import {onMount} from "svelte";

    export let events: {time: number, comp: string, type: string}[];

    /*let events = [
        { time: 4, comp: "comp1", type: "MESSAGE_SENT" },
        { time: 10, comp: "comp2", type: "MESSAGE_RECV" },
        { time: 12, comp: "comp1", type: "MESSAGE_SENT" },
        { time: 40, comp: "comp1", type: "COMP" },
    ];*/

    let minTs = 0;
    let maxTs = 0;

    let tracks = new Map<string, any[]>();

    for (let ev of events) {
        if (!tracks.has(ev.comp)) tracks.set(ev.comp, []);
        tracks.get(ev.comp).push(ev);
        if (ev.time < minTs) minTs = ev.time;
        if (ev.time > maxTs) maxTs = ev.time;
    }

    let markers = new Map<string, any[]>();

    for (let [comp, evs] of tracks) {
        evs.sort((ev1, ev2) => ev1.time - ev2.time);
        markers.set(comp, []);
        let i = 0;
        let ev = evs[i];
        let currentMarker = {
            time: ev.time,
            evs: [ev],
            el: undefined,
        };
        i++
        for (; i < evs.length; i++) {
            ev = evs[i];
            if (ev.time == currentMarker.time) {
                currentMarker.evs.push(ev);
                continue;
            }
            markers.get(comp).push(currentMarker);
            currentMarker = {
                time: ev.time,
                evs: [ev],
                el: undefined,
            }
        }
        markers.get(comp).push(currentMarker);
    }

    const TIME_PAD_PERC = 25;

    let dur = maxTs - minTs;
    minTs -= TIME_PAD_PERC/100 * dur;
    maxTs += TIME_PAD_PERC/100 * dur;

    $: resolution = 1; // 1 == full width for max-min
    //$: centerOffset = offset

    // for resolution = 1: em_per_ts s.t. using full window
    // resolution > 1: em_per_ts ++
    // resolutino < 1: em_per_ts --
    let base_em_per_ts = 1;
    $: em_per_ts = resolution * base_em_per_ts;

    let px_per_em = 1;
    let timelineEl;

    onMount(() => {
        px_per_em = parseFloat(getComputedStyle(timelineEl).fontSize);
        let bb: DOMRect = timelineEl.getBoundingClientRect();
        let widthPx = bb.width;
        let totalTs = maxTs - minTs;
        base_em_per_ts = (widthPx / totalTs) / px_per_em;
    });

    let cursorMarker;
    let cursorMarkerVisible = false;

    $: offset = 0;

    $: cursorTs = ((mouseOffs + offset) / px_per_em) / em_per_ts + minTs;

    $: virtMaxTs = maxTs; // Math.max(maxTs, cursorTs);

    $: prec = 2;

    let mouseOffs = 0;

    function hover(ev) {
        selection.endX = offset + ev.clientX;
        cursorMarkerVisible = true;
        mouseOffs = ev.clientX;
    }

    $: timelineWidthEm = (virtMaxTs - minTs) * em_per_ts;

    $: ticks = [];

    $: {
        ticks = [];
        let interval = (dur / resolution) / 5; // last digit should be either .0, .1, .5
        prec = Math.max(2, -Math.ceil(Math.log10(interval)) + 1);
        interval = interval - (interval % 10**(-prec+1));
        //console.log(interval, iv, prec);
        let start = minTs + Math.abs((minTs + interval) % interval);
        //console.log("start", start, minTs);
        //let start = minTs;
        for (let t = start; t <= virtMaxTs; t += interval) {
            ticks.push({
                t: t,
                text: t.toFixed(prec) + "ms"
            });
        }
    }

    function scroll(ev: Event) {
        let mouseX = selection.endX - offset;
        offset = timelineEl.scrollLeft;
        selection.endX = offset + mouseX;
    }

    function setResolution(res) {
        let currCenterOffs = offset + timelineEl.getBoundingClientRect().width / 2;
        resolution = res;
        currCenterOffs *= 1.1;
        let newOffset = currCenterOffs - timelineEl.getBoundingClientRect().width / 2;
        requestAnimationFrame(() => { // need to wait until track width is recalculated by browser
            timelineEl.scrollTo({
                left: newOffset,
                behavior: "instant",
            });
        });

    }

    function keydown(ev: KeyboardEvent) {
        if (ev.ctrlKey && ev.key == "+") {
            setResolution(resolution * 1.1);
            ev.preventDefault();
        } else if (ev.ctrlKey && ev.key == "-") {
            if (resolution == 1) {
                ev.preventDefault();
                return;
            }
            setResolution(Math.max(1, resolution / 1.1));
            ev.preventDefault();
            return;
        }
    }

    function resized(ev: Event) {
        px_per_em = parseFloat(getComputedStyle(timelineEl).fontSize);
        let bb: DOMRect = timelineEl.getBoundingClientRect();
        let widthPx = bb.width;
        let totalTs = maxTs - minTs;
        base_em_per_ts = (widthPx / totalTs) / px_per_em;
    }

    let markerTooltip = {
        visible: false,
        left: 0,
        top: 0,
        evs: [],
        t: 0,
    }

    let selection = {
        startX: 0,
        endX: 0,
        leftStart: 0,
        width: 0,
        visible: false,
    }

    $: selection.leftStart = Math.min(selection.startX, selection.endX);
    $: selection.width = Math.abs(selection.endX - selection.startX);

    function markerHover(ev: MouseEvent, marker) {
        markerTooltip.left = ev.clientX + px_per_em;
        markerTooltip.top = ev.clientY + px_per_em;
        markerTooltip.visible = true;
        markerTooltip.evs = marker.evs;
        markerTooltip.t = marker.time;
    }

    function startSelection(ev: MouseEvent) {
        console.log(ev.target);
        selection.startX = offset + ev.clientX;
        selection.endX = offset + ev.clientX;
        selection.visible = true;
    }

    function select(ev) {
        console.log("select", selection.leftStart, selection.width);
        selection.visible = false;
        if (selection.width < 10) return;
        // resolution = 1 <=> dur <=> full-width
        // we want to calc the resolution s.t. selection.width == new_width
        let w = selection.width / (timelineWidthEm * px_per_em);
        // == res_target / res_curr
        let old_res = resolution;
        let new_res = resolution / w;
        console.log(resolution / w);
        setResolution(resolution / w);
        requestAnimationFrame(() => { // need to wait until track width is recalculated by browser
            timelineEl.scrollTo({
                left: (selection.leftStart / old_res) * new_res,
                behavior: "instant",
            });
        });
    }
</script>

<svelte:window on:keydown={keydown} on:resize={resized}/>

<div style="overflow: hidden; width:100%; height:100%; position: relative">

<div id="markerToolTip" class:hidden={!markerTooltip.visible} style:transform={`translate(${markerTooltip.left}px, ${markerTooltip.top}px)`}>
    <p>{markerTooltip.t.toFixed(prec)}ms</p>
    {#each markerTooltip.evs as ev}
        <li>{ev.type}: {ev.data}</li>
    {/each}
</div>
<div bind:this={cursorMarker} class:hidden={!cursorMarkerVisible} class="cursor-marker"
        style:transform={"translateX(" + (mouseOffs) + "px)"}>
    {cursorTs.toFixed(prec)}ms
</div>
<div bind:this={timelineEl} on:scroll={scroll} id="timeline" on:mousemove={hover} on:mouseleave={(ev) => {cursorMarkerVisible=false}}
    on:mousedown={startSelection} on:mouseup={select}
>
    <div id="selection" class:hidden={!selection.visible}
        style:transform={`translateX(${selection.leftStart}px)`} style:width={selection.width + "px"}>
    </div>
    <div id="time-ticks" class:faded={true} style="width: {timelineWidthEm + 'em'}">
        {#each ticks as tick}
            <div class="event-marker" style="transform: translate({(tick.t - minTs) * em_per_ts}em)">
                {tick.text}
            </div>
        {/each}
    </div>
    <div id="sep"></div>
    {#each markers as [comp, ms]}
        <div class="track">
            <div class="track-name">
                <p>{comp}</p>
            </div>
            <div class="events" style="width: {timelineWidthEm + 'em'}">
            {#each ms as marker}
                <div bind:this={marker.el} on:mousemove={(ev) => {markerHover(ev,marker)}}
                     on:mouseleave={() => markerTooltip.visible = false}
                     class="event-marker" style="transform: translate({(marker.time - minTs) * em_per_ts}em)">

                </div>
            {/each}
        </div>
    </div>
    {/each}
</div>

</div>

<style>
    * {
        font-family: sans-serif;
    }

    #timeline {
        position: relative;
        width: 100%;
        height: 100%;

        background-size: 20px 20px;
        background-image:  repeating-linear-gradient(to right, rgba(0,0,0,.1), rgba(0,0,0,.1) 1px, rgba(255,255,255,0) 1px, rgba(255,255,255,0));

        user-select: none;

        overflow-x: scroll;
    }

    #time-ticks {
        height: 2em;
        position: sticky;
        overflow-x: hidden;
    }

    #time-ticks.faded {
        opacity: .3;
    }

    .track {
        margin: 1em 0;
    }

    .track-name {
        opacity: .7;
        display: flex;
        height: 5em;
        position: fixed;
        flex-direction: column;
        justify-content: center;
        padding: 0 .2em;
        z-index: 9;
        background-color: white;
        border: 1px solid black;
        box-sizing: border-box;
    }

    .track-name p {
        transform: translateY(-.1em);
    }

    #sep {
        height: 1em;
        width: 100%;
    }

    #selection {
        width: 1px;
        height: 100%;
        background-color: #6ab0de;
        opacity: .3;
        position: absolute;
        z-index: 8;
        pointer-events: none;
    }

    #markerToolTip {
        position: absolute;
        background-color: white;
        border: .1em solid gray;
        display: flex;
        flex-direction: column;
        padding: .5em;
        z-index: 10;
    }

    #markerToolTip p {
        margin: 0;
        margin-bottom: .5em;
        font-weight: bold;
    }

    #markerToolTip li {
        list-style: none;
    }

    .events {
        height: 5em;
        position: relative;
        background-color: rgba(0, 0, 0, 0.1);
        overflow-x: hidden;
    }

    .event-marker {
        position: absolute;
        top: 10%;
        bottom: 10%;
        border-left: .1em solid black;
        width: 0;
    }

    .event-marker::after {
        content: "";
        width: 1em;
        position: absolute;
        height: 100%;
        transform: translateX(-50%);
    }

    .event-marker:hover {

        color: cornflowerblue;
        border-color: cornflowerblue;
    }

    .cursor-marker {
        position: absolute;
        height: 100%;
        padding-left: .2em;
        width: 4px;

        border-left: .1em solid darkgray;
    }

    .hidden {
        display: none !important;
    }

</style>