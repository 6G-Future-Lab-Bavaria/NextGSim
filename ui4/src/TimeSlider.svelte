<script lang="ts">

    import {createEventDispatcher, onMount} from "svelte";

    export let absoluteMinTs: number;
    export let absoluteMaxTs: number;
    export let trackLive: boolean;
    export let cursorPos_ts: number | null;
    export let selectedPos_ts: number;

    let minTs = absoluteMinTs;
    let maxTs = absoluteMaxTs;

    $: {
        absoluteMinTs;
        if (trackLive) {
            minTs = absoluteMinTs;
            recalculateTime();
            fireChangeEvent();
        }
    }

    $: {
        absoluteMaxTs;
        if (trackLive) {
            maxTs = absoluteMaxTs;
            recalculateTime();
            fireChangeEvent();
        }
    }

    const dispatch = createEventDispatcher<{onChange:{minTs:number, maxTs:number}}>();
    function fireChangeEvent() {
        dispatch("onChange", {minTs, maxTs});
    }

    $: {
        absoluteMaxTs;
        recalculateGlobalPositionIndicator();
    }
    $: {
        absoluteMinTs;
        recalculateGlobalPositionIndicator();
    }

    export let isLive: boolean = false;
    let range = maxTs - minTs;

    let handleLeftOffset = 0;
    let handleRightOffset = 0;

    let cursorOffset = 50;
    let cursorVisible = false;

    let tm: number | null = null;
    let expandTimeframeIntv: number | null = null;

    let rel: HTMLDivElement;
    let timelineWidthPx: number = 0;
    let timelineLeftOffset: number = 0;
    let timelineRightOffset: number = 0;

    let ticks: { time: string, offset: number, widthPx: number, label: string | null }[] = []

    let globalPosIndicatorRelWidth = 0;
    let globalPosIndicatorRelLeftOffset = 0;

    function recalculateGlobalPositionIndicator() {
        console.log("recalculateGlobalPositionIndicator");

        let totalDuration = absoluteMaxTs - absoluteMinTs;
        let currentDuration = maxTs - minTs;

        globalPosIndicatorRelWidth = currentDuration / totalDuration;
        globalPosIndicatorRelLeftOffset = (minTs - absoluteMinTs) / totalDuration;
    }

    function recalculateTime() {
        // 9-10 ticks all the time
        range = maxTs - minTs;
        let tks = []

        // if range >= 2s:

        // seconds
        let tickWidthMs = 100; //range / 10;
        let tickWidthPx = timelineWidthPx / (range / tickWidthMs);

        for (let t = Math.ceil(minTs / 100) * 100, offset = 0; t < maxTs; t += tickWidthMs, offset += tickWidthPx) {
            tks.push({
                time: t.toFixed(2),
                offset: offset,
                widthPx: t % 1000 === 0 ? 2 : 1,
                label: t % 1000 === 0 ? Math.round(t / 1000) + "" : null,
            });
        }
        ticks = tks;

        // if range < 2s:
        // big-ticks: 100ms steps, small-ticks: 10ms

        recalculateGlobalPositionIndicator();
    }

    onMount(() => {
        timelineWidthPx = rel.getBoundingClientRect().width;
        timelineLeftOffset = rel.getBoundingClientRect().left;
        timelineRightOffset = rel.getBoundingClientRect().right;
        handleRightOffset = timelineWidthPx;

        recalculateTime();
        fireChangeEvent();
    });

    function onOver(ev: MouseEvent) {
        //cursorVisible = true;
        //cursorOffset = ev.clientX;

        if (grabbing == "left") {
            if (ev.clientX < timelineLeftOffset) {
                handleLeftOffset = 0;
                let factor = (timelineLeftOffset - ev.clientX) / timelineLeftOffset;

                if (expandTimeframeIntv === null) {
                    // @ts-ignore
                    expandTimeframeIntv = setInterval(() => {
                        minTs -= (maxTs - minTs) * factor;
                        minTs = Math.max(absoluteMinTs, minTs);
                        recalculateTime();
                    }, 100);
                }
                return;
            }

            if (expandTimeframeIntv !== null) {
                clearInterval(expandTimeframeIntv);
                expandTimeframeIntv = null;
            }

            let bounded = Math.min(Math.max(0, ev.clientX - timelineLeftOffset), timelineWidthPx);
            handleLeftOffset = bounded;
        } else if (grabbing == "right") {
            if (ev.clientX > timelineRightOffset) {
                handleRightOffset = timelineWidthPx;
                let factor = (ev.clientX - timelineRightOffset) / timelineRightOffset;

                if (expandTimeframeIntv === null) {
                    // @ts-ignore
                    expandTimeframeIntv = setInterval(() => {
                        maxTs += (absoluteMaxTs - absoluteMinTs) * factor;
                        maxTs = Math.min(absoluteMaxTs, maxTs);
                        recalculateTime();
                    }, 100);
                }
                return;
            }

            if (expandTimeframeIntv !== null) {
                clearInterval(expandTimeframeIntv);
                expandTimeframeIntv = null;
            }

            let bounded = Math.min(Math.max(0, ev.clientX - timelineLeftOffset), timelineWidthPx);
            handleRightOffset = bounded;
        }
    }

    function onOut(ev: MouseEvent) {
        cursorVisible = false;
        if (expandTimeframeIntv !== null) {
            clearInterval(expandTimeframeIntv);
            expandTimeframeIntv = null;
        }
    }

    function onUp(ev: MouseEvent) {
        if (!grabbing) {
            let pos_ts = calcPosTsFromClientX(ev.clientX);
            if (pos_ts >= minTs && pos_ts < maxTs)
                selectedPos_ts = pos_ts;
            return;
        }

        let tmp = grabbing;
        grabbing = null;

        if (expandTimeframeIntv !== null) {
            clearInterval(expandTimeframeIntv);
            expandTimeframeIntv = null;
        }

        // @ts-ignore
        tm = setTimeout(() => {
            if (tmp == "left") {
                let timeStart = (handleLeftOffset / timelineWidthPx) * (maxTs - minTs);
                timeStart = minTs + Math.min(maxTs - 1e-5, timeStart);
                minTs = timeStart;
                handleLeftOffset = 0;
                recalculateTime();
                fireChangeEvent();
            } else {
                let timeEnd = (handleRightOffset / timelineWidthPx) * (maxTs - minTs);
                timeEnd = minTs + Math.max(1e-5, timeEnd);
                maxTs = timeEnd
                handleRightOffset = timelineWidthPx;
                recalculateTime();
                fireChangeEvent();
            }
        }, 1000);
    }

    let grabbing: string | null = null;

    function onHandleGrab(which: string) {
        return (ev: MouseEvent) => {
            grabbing = which;
            if (tm !== null) {
                clearTimeout(tm);
                tm = null;
            }
        }
    }

    function calcPosTsFromClientX(clientX: number) {
        let trackX = rel.getBoundingClientRect().x;
        let trackWidth = rel.getBoundingClientRect().width;
        let x = clientX - trackX;
        let relX = x / trackWidth;
        return relX * (maxTs - minTs) + minTs;
    }

    function mouseMoveRel(ev: MouseEvent) {
        cursorPos_ts = calcPosTsFromClientX(ev.clientX);
    }

    function calcCursorPos_px(cursorPos_ts: number) {
        let trackWidth = rel.getBoundingClientRect().width;
        return trackWidth * (cursorPos_ts - minTs) / (maxTs - minTs);
    }

</script>

<div id="container" on:mousemove={onOver} on:mouseleave={onOut} on:mouseup={onUp}>
    <div id="rel" bind:this={rel} on:mousemove={mouseMoveRel} on:mouseleave={() => cursorPos_ts = null}>
        {#if rel !== undefined && cursorPos_ts !== null}
            <div id="cursor" style:left="{calcCursorPos_px(cursorPos_ts)}px"></div>
        {/if}
        {#if rel !== undefined}
            <div id="selection" style:left="{calcCursorPos_px(selectedPos_ts)}px"></div>
        {/if}

        {#each ticks as tick}
            <div class="tick" style:transform="translateX({tick.offset}px)" style:border-left="{tick.widthPx}px solid teal">
                {#if tick.label}
                    {tick.label}
                {/if}
            </div>
        {/each}

        <div id="left" style:transform="translateX({handleLeftOffset}px)" class="handle"
            on:mousedown={onHandleGrab("left")}
        >
        </div>
        <div id="cursor" style:visibility={cursorVisible ? "visible" : "hidden"}
             style:transform="translateX({cursorOffset}px)"
        >

        </div>
        <div id="right" style:transform="translateX({handleRightOffset}px)" class="handle"
            on:mousedown={onHandleGrab("right")} style:background-color={isLive ? "green" : "gray"}
        >

        </div>

        <div id="global-scale">
            <div id="relative-position-indicator"
                style:transform="translateX({Math.min(globalPosIndicatorRelLeftOffset,.99)*100}%)"
                style:width="{Math.max(globalPosIndicatorRelWidth, .01)*100}%"
            ></div>
        </div>
    </div>
</div>

<style>
    #container {
        height: 4em;
        width: 100%;
        background-color: #eeeeee;
        user-select: none;
    }

    #rel {
        position: relative;
        width: 90%;
        height: 100%;
        margin-left: 5%;
        pointer-events: all;
    }

    .tick {
        position: absolute;
        border-left: 2px solid teal;
        padding-left: .1em;
        pointer-events: none;
        height: 1.5em;
        font-weight: bold;
    }

    .handle {
        position: absolute;
        top: .5em;
        bottom: .5em;
        width: 2px;
        cursor: grab;
        background-color: gray;
    }

    .handle:after {
        position: absolute;
        content: "";
        width: 2em;
        height: 100%;
        cursor: grab;
        transform: translateX(-50%);
    }

    #cursor {
        position: absolute;
        top: 0;
        bottom: 0;
        width: 2px;
        background-color: black;
        transform: translateX(-50%);
    }

    #selection {
        position: absolute;
        top: 0;
        bottom: 0;
        width: 2px;
        background-color: teal;
        border-left: 2px solid black;
        border-right: 2px solid black;
        transform: translateX(-50%);
    }

    #global-scale {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background-color: grey;
    }

    #relative-position-indicator {
        position: absolute;
        background-color: black;
        top: 0;
        bottom: 0;
        min-width: 10px;
    }
</style>