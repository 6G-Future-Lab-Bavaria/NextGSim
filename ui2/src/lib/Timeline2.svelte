<script lang="ts">
    import {onMount} from "svelte";

    export let tracks_: { [key: string] : {
        events: {time: number, comp: string, type: string}[]
    }} = {};

    //export let events: {time: number, comp: string, type: string}[];

    $: tracks = getTracks(tracks_);
    let trackEls = {};

    function getTracks(tracks_: any) {
        return Object.entries(tracks_).map(([c,t]) => {
            return {
                comp: c,
                // @ts-ignore
                events: t.events,
                el: undefined,
            }
        });
    }

    function getTimeTicks(fromT, toT) {

        let timeInterval = toT - fromT;

        let markers = [];

        let ts: any[] = [
            [60*60*1000, 2, "h"],
            [60*1000, 2, "m"],
            [1000, 2, "s"],
            [100, 0, "ms"],
            [10, 0, "ms"],
            [5, 0, "ms"],
            [1, 0, "ms"],
            [.5, 0, "ms"],
            [.1, 0, "ms"],
        ];

        for (let [t,prec,tick] of ts) {
            if (timeInterval > 1 * t) {
                for (let i = Math.ceil(fromT / t) * t; i < toT; i += t) {
                    markers.push({
                        t: i,
                        //type: "100ns",
                        tick: i.toFixed(prec) + tick,
                        //interval: 0.01,
                    });
                }
                break;
            }
        }

        /*

        // can be optimized
        if (timeInterval <= .05) {
            // 10ns marker
            // 1., 1.01, 1.02
            for (let i = Math.ceil(fromT * 100) / 100; i < toT; i += 0.01) {
                markers.push({
                    t: i,
                    type: "100ns",
                    tick: i.toFixed(2) + "ms",
                    interval: 0.01,
                });
            }
        }
        else if (timeInterval <= .5) {
            // 100ns marker
            // 1., 1.01, 1.02
            for (let i = Math.ceil(fromT * 10) / 10; i < toT; i += 0.1) {
                markers.push({
                    t: i,
                    type: "100ns",
                    tick: i.toFixed(1) + "ms",
                    interval: 0.1,
                });
            }
        } else if (timeInterval <= 5) {
            // ms markers
            // if fromT % 1 == 0 => include, otheri
            for (let i = Math.ceil(fromT); i < toT; i++) {
                markers.push({
                    t: i,
                    type: "tick",
                    tick: i.toFixed(0) + "ms",
                    interval: 1,
                });
            }
        } else { // (timeInterval <= 50) {  // 10ms
            // ms markers
            // if fromT % 1 == 0 => include, otheri
            for (let i = Math.ceil(fromT / 10) * 10; i < toT; i += 10) {
                markers.push({
                    t: i,
                    type: "tick",
                    tick: i.toFixed(0) + "ms",
                    interval: 1,
                });
            }
        } /*else { // 100 ms
            for (let i = Math.ceil(fromT / 100) * 100; i < toT; i += 100) {
                markers.push({
                    t: i,
                    type: "tick",
                    tick: i.toFixed(0) + "ms",
                    interval: 1,
                });
            }
        }*/

        markers.sort((a,b) => a.t - b.t);
        return markers;
    }

    let tiles = [];

    const TIME_PAD_PERC = 25;
    const NUM_TILES = 10; // loaded = #children in tile-container
    const NUM_TILES_SCROLL_PAD = 3; // 4 tiles in screen

    // left and right NUM_TILES_SCROLL_PAD
    let tilesOnScreen = NUM_TILES - 2 * NUM_TILES_SCROLL_PAD; // #tiles

    let totalInterval = [0, 1];
    let currentInterval = totalInterval;
    let totalTiles;
    let currentIntervalStartTile;
    let intervalPerTile;
    let prec;

    let screenWidth = 0;

    let timelineEl: HTMLDivElement;
    let tileContainerEl: HTMLDivElement;

    $: {
        console.log("UPDATE");

        let minTs = 0;
        let maxTs = 0;

        for (let track of Object.values(getTracks(tracks_))) {
            for (let ev of track.events) {
                if (ev.time < minTs) minTs = ev.time;
                if (ev.time > maxTs) maxTs = ev.time;
            }
        }

        maxTs = Math.max(minTs + 100, maxTs);

        let timePad = TIME_PAD_PERC/100 * (maxTs - minTs);
        totalInterval = [minTs - timePad, maxTs + timePad];
    }

    $: currentInterval = [totalInterval[0], totalInterval[1]];

    $: {
        intervalPerTile = (currentInterval[1] - currentInterval[0]) / tilesOnScreen // interval

        totalTiles = Math.ceil((totalInterval[1] - totalInterval[0]) / intervalPerTile); // #tiles

        currentIntervalStartTile = Math.floor(currentInterval[0] / intervalPerTile);

        prec = Math.max(2, -Math.log10(intervalPerTile / 5) + 1);
    }

    $: tileWidth = screenWidth / tilesOnScreen; // px per tile

    function getMarkersInRange(track, fromT, toT) {
        let markers = [];
        let evs = track.events;
        if (evs.length == 0) return markers; // shouldnt happen

        let i = 0;
        let ev = evs[i];
        let currentMarker = {
            comp: track.comp,
            time: ev.time,
            evs: [ev],
            el: undefined,
            offsetTop: trackEls[track.comp].offsetTop,
        };
        i++

        for (; i < evs.length; i++) {
            ev = evs[i];
            if (ev.time == currentMarker.time) {
                currentMarker.evs.push(ev);
                continue;
            }
            markers.push(currentMarker);
            currentMarker = {
                comp: track.comp,
                 time: ev.time,
                 evs: [ev],
                 el: undefined,
                 offsetTop: trackEls[track.comp].offsetTop,
            }
        }

        return markers;
    }

    // $: {console.log(tracks.map(t => t.comp), tracks_, trackEls);}

    // need to ensure that this is not clogging everything
    // consider eg. loading events once user stops scrolling
    function ensureTilesLoaded(fromI, toI) { // inclusive
        fromI = Math.max(0, fromI);
        toI = Math.min(totalTiles-1, toI);

        let newTiles = [];

        for (let i = fromI; i <= toI; i++) {
            let minTimeInc = totalInterval[0] + i * intervalPerTile;
            let maxTimeExc = totalInterval[0] + (i+1) * intervalPerTile;
            let currMarkers = [];

            for (let track of tracks) {
                for (let event of track.events) {
                     if (event.time >= minTimeInc && event.time < maxTimeExc)
                         currMarkers.push({
                             comp: track.comp,
                             time: event.time,
                             evs: [event],
                             el: undefined,
                         });
                }
            }

            newTiles.push({
                i: i,
                markers: currMarkers, // todo remove, unused, actually whole function can be ~removed
            });
        }

        tiles = newTiles;
    }

    onMount(() => {
        screenWidth = timelineEl.clientWidth

        ensureTilesLoaded(currentIntervalStartTile - NUM_TILES_SCROLL_PAD, currentIntervalStartTile + NUM_TILES + NUM_TILES_SCROLL_PAD);

        requestAnimationFrame(() =>
            timelineEl.scrollTo({left: getOffsetForTime(currentInterval[0])})
        );
    });

    function onScrollTiles(ev: Event) {
        let offsetLeft = timelineEl.scrollLeft;

        let visibleLeft = Math.round(offsetLeft);
        let visibleRight = Math.round(offsetLeft + timelineEl.clientWidth);

        let visibleLeftI = Math.floor(visibleLeft / tileWidth);
        let visibleRightI = Math.floor(visibleRight / tileWidth);

        ensureTilesLoaded(visibleLeftI - NUM_TILES_SCROLL_PAD, visibleRightI + NUM_TILES_SCROLL_PAD);
    }

    function getTimeAtMiddle() {
        let middleOffset = timelineEl.scrollLeft + timelineEl.clientWidth / 2;
        let adjDur = totalTiles * intervalPerTile;
        let middleTime = totalInterval[0] + adjDur * middleOffset / timelineEl.scrollWidth;
        return middleTime;
    }

    function getOffsetForTime(time) {
        let width = tileContainerEl.offsetWidth;
        let adjDur = totalTiles * intervalPerTile;
        let offset = width * ((time - totalInterval[0]) / adjDur);
        return offset;
    }

    function getTimeAtOffset(offset) {
        let width = tileContainerEl.offsetWidth;
        let adjDur = totalTiles * intervalPerTile;
        return totalInterval[0] + (offset / width) * adjDur;
    }

    function onKeydown(ev: KeyboardEvent) {
        if (ev.ctrlKey && ev.key == "+") { // zoom in
            ev.preventDefault();
            // find current middle offset and thus time
            //let middleOffset = time
            let middleTime = getTimeAtMiddle();

            let halfInterval = .5 * (currentInterval[1] - currentInterval[0]);
            //let middleTime = currentInterval[0] + halfInterval;
            let reducedInterval = halfInterval * .8;
            currentInterval = [middleTime - reducedInterval, middleTime + reducedInterval];
            //ensureTilesLoaded(currentIntervalStartTile - NUM_TILES_SCROLL_PAD, currentIntervalStartTile + NUM_TILES + NUM_TILES_SCROLL_PAD);

            // scroll so that no shift
            requestAnimationFrame(() => {
                timelineEl.scrollTo({left: getOffsetForTime(currentInterval[0])});
            });

        } else if (ev.ctrlKey && ev.key == "-") { // zoom out
            ev.preventDefault();
            if (currentInterval[0] == totalInterval[0] && currentInterval[1] == totalInterval[1]) {
                return;
            }
            let middleTime = getTimeAtMiddle();

            let halfInterval = .5 * (currentInterval[1] - currentInterval[0]);
            //let middleTime = currentInterval[0] + halfInterval;
            let increasedInterval = halfInterval / .8;
            let left = Math.max(totalInterval[0], middleTime - increasedInterval);
            let right = Math.min(totalInterval[1], middleTime + increasedInterval);
            if (left == totalInterval[0] && right < totalInterval[1])
                currentInterval = [left, left + 2*increasedInterval];
            else if (right == totalInterval[1] && left > totalInterval[0])
                currentInterval = [right - 2*increasedInterval, right];
            else
                currentInterval = [left, right];

            console.log(currentInterval)

            //currentInterval = [Math.max(totalInterval[0], middleTime - increasedInterval), Math.min(totalInterval[1], middleTime + increasedInterval)];
            let adjFirstHalf = (currentInterval[1] - currentInterval[0]) / 2;
            let leftTime = Math.max(totalInterval[0], middleTime - adjFirstHalf);

            ensureTilesLoaded(currentIntervalStartTile - NUM_TILES_SCROLL_PAD, currentIntervalStartTile + NUM_TILES + NUM_TILES_SCROLL_PAD);
            requestAnimationFrame(() => {
                //timelineEl.scrollTo({left: 0});
                /*requestAnimationFrame(() => {
                    timelineEl.scrollTo({left: getOffsetForTime(leftTime)});
                });*/
                timelineEl.scrollTo({left: getOffsetForTime(leftTime)});
            });
        }
    }

    function onResize() {
        screenWidth = timelineEl.clientWidth;
    }

    function action(node, comp) {
        trackEls[comp] = node;
        return {
            update: (newC) => {
                delete trackEls[comp];
                trackEls[newC] = node;
            },
            destroy: () => {
                delete trackEls[comp];
            }

        }
    }

    let markerTooltip = {
        visible: false,
        left: 0,
        top: 0,
        evs: [],
        t: 0,
    }

    function markerHover(ev: MouseEvent, marker) {
        let bb = timelineEl.getBoundingClientRect();
        markerTooltip.left = ev.clientX - bb.left + 10;
        markerTooltip.top = ev.clientY - bb.top + 10;
        markerTooltip.visible = true;
        markerTooltip.evs = marker.evs;
        markerTooltip.t = marker.time;
    }
    
    let windowWidth;
    let windowHeight;

    let selection = {
        startX: 0,
        endX: 0,
        leftStart: 0,
        width: 0,
        visible: false,
        fromT: 0,
        toT: 0,
    }

    $: selection.leftStart = Math.min(selection.startX, selection.endX);
    $: selection.width = Math.abs(selection.endX - selection.startX);

    function startSelection(ev: MouseEvent) {
        console.log(ev);
        let bb = timelineEl.getBoundingClientRect();
        selection.startX = timelineEl.scrollLeft + ev.clientX - bb.left;
        selection.fromT = getTimeAtOffset(selection.startX);
        selection.endX = timelineEl.scrollLeft + ev.clientX - bb.left;
        selection.toT = getTimeAtOffset(selection.endX);
        selection.visible = true;
    }

    function hover(ev: MouseEvent) {
        let bb = timelineEl.getBoundingClientRect();
        selection.endX = timelineEl.scrollLeft + ev.clientX - bb.left;
        selection.toT = getTimeAtOffset(selection.endX);
    }

    function select(ev) {
        selection.visible = false;
        if (selection.width < 10) return;

        let fromT = Math.min(selection.fromT, selection.toT);
        let toT = Math.max(selection.fromT, selection.toT);

        console.log(fromT, toT);

        // here width check, todo
        currentInterval = [fromT, toT];

        requestAnimationFrame(() => {
            timelineEl.scrollTo({left: getOffsetForTime(currentInterval[0])});
        });
    }
</script>

<svelte:window on:keydown={onKeydown} on:resize={onResize} bind:innerWidth={windowWidth} bind:innerHeight={windowHeight}></svelte:window>

<div id="container">
    <div id="markerToolTip" class:hidden={!markerTooltip.visible} style:transform={`translate(${markerTooltip.left}px, ${markerTooltip.top}px)`}>
        <p>{markerTooltip.t.toFixed(prec)}ms</p>
        {#each markerTooltip.evs as ev}
            <li><b>{ev.type}:</b>
                {#if ev.data != null}
                {ev.data}
                {:else}
                    <i>no data</i>
                {/if}
            </li>
        {/each}
    </div>

    <div class="tracks">
        {#each tracks as track (track.comp)}
            <div class="track overlay" use:action={track.comp}>
                <div class="track-name">
                    {track.comp}
                </div>
            </div>
        {/each}
    </div>

    <div bind:this={timelineEl}
         on:mousedown={startSelection} on:mousemove={hover} on:mouseup={select}
         on:scroll|passive={onScrollTiles} id="timeline">
        <div id="overlay">
        </div>
        <div id="selection" class:hidden={!selection.visible}
            style:transform={`translateX(${selection.leftStart}px)`} style:width={selection.width + "px"}>
        </div>
        <div bind:this={tileContainerEl} style:width="{totalTiles * tileWidth}px" id="tile-container">
            {#each tiles as tile}
            <div class="tile" class:other={false && tile.i % 2} style:width={tileWidth + "px"} style:transform={"translateX(" + tile.i * tileWidth + "px)"}>
                {#each getTimeTicks(totalInterval[0] + tile.i * intervalPerTile, totalInterval[0] + (tile.i+1) * intervalPerTile) as marker}
                    <div class="time-marker" style:transform="translateX({(marker.t - (totalInterval[0] + tile.i * intervalPerTile)) / intervalPerTile * tileWidth}px)">
                        <p>{marker.tick}</p>
                    </div>
                {/each}
                <div class="tracks">
                    {#each tracks as track (track.comp)}
                        <div class="track">
                            {#each getMarkersInRange(track, totalInterval[0] + tile.i * intervalPerTile, totalInterval[0] + (tile.i+1) * intervalPerTile) as marker}
                            <div class="marker"
                                 style:transform="translateX({ (marker.time - (totalInterval[0] + tile.i * intervalPerTile)) / intervalPerTile * tileWidth}px) translateX(-50%)"
                                on:mousemove={(ev) => {markerHover(ev, marker)}} on:mouseleave={() => markerTooltip.visible = false}
                            >
                            </div>
                            {/each}
                        </div>
                    {/each}
                </div>
            </div>
            {/each}
        </div>
    </div>
</div>

<style>
    #container {
        width: 100%;
        min-height: 100%;
        position: relative;
    }

    .tracks {
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        padding-top: 4em;
        box-sizing: border-box;
    }

    .track {
        height: 5em;
        margin-bottom: 2em;
        position: relative;
    }

    .track:last-child {
        margin-bottom: 0;
    }

    .track.overlay {
        background-color: rgba(128, 128, 128, 0.15);
    }

    .track-name {
        font-weight: bold;
        position: absolute;
        left: .5em;
        top: 0;
        transform: translateY(-110%);
    }

    #timeline {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 100%;
        overflow-x: scroll;
        user-select: none;
    }

    #tile-container {
        height: 100%;
        position: relative;
        overflow-x: hidden;
    }

    .tile {
        height: 100%;
        position: absolute;
        top: 0;
        left: 0;
    }

    .time-marker {
        position: absolute;
        top: 2em;
        bottom: 0;
        width: 1px;
        font-size: .8em;
        opacity: .25;
        background-color: black;
    }

    .time-marker * {
        transform: translateX(-1em) translateY(-3em);
    }

    .tile.other {
        background-color: #1abc9c;
    }

    .marker {
        position: absolute;
        top: 10%;
        bottom: 10%;
        background-color: black;
        width: 3px;
    }

    .marker::after {
        content: "";
        width: 1em;
        position: absolute;
        height: 100%;
        transform: translateX(-50%);
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

    #markerToolTip.hidden {
        display: none;
    }

    #markerToolTip p {
        margin: 0;
        margin-bottom: .5em;
        font-weight: bold;
    }

    #markerToolTip li {
        list-style: none;
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

    #selection.hidden {
        display: none;
    }
</style>