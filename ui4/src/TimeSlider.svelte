<script lang="ts">

    import {onMount} from "svelte";

    export let absoluteMinTs: number;
    export let absoluteMaxTs: number;

    let minTs = absoluteMinTs;
    let maxTs = absoluteMaxTs;

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

    let ticks: { time: string, offset: number }[] = []

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
        let tickWidthMs = range / 10;
        let tickWidthPx = timelineWidthPx / (range / tickWidthMs);

        for (let t = minTs, offset = 0; t < maxTs; t += tickWidthMs, offset += tickWidthPx) {
            tks.push({
                time: t.toFixed(2),
                offset: offset
            });
        }
        ticks = tks;

        recalculateGlobalPositionIndicator();
    }

    onMount(() => {
        timelineWidthPx = rel.getBoundingClientRect().width;
        timelineLeftOffset = rel.getBoundingClientRect().left;
        timelineRightOffset = rel.getBoundingClientRect().right;
        handleRightOffset = timelineWidthPx;

        recalculateTime();
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
                        maxTs += (maxTs - minTs) * factor;
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
            } else {
                let timeEnd = (handleRightOffset / timelineWidthPx) * (maxTs - minTs);
                timeEnd = minTs + Math.max(1e-5, timeEnd);
                maxTs = timeEnd;
                handleRightOffset = timelineWidthPx;
                recalculateTime();
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

</script>

<div id="container" on:mousemove={onOver} on:mouseleave={onOut} on:mouseup={onUp}>
    <div id="rel" bind:this={rel}>
        {#each ticks as tick}
            <div class="tick" style:transform="translateX({tick.offset}px)">
                {tick.time} Ts
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
        padding-left: .5em;
        pointer-events: none;
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
        background-color: teal;
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