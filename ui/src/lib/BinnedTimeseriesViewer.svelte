<script lang="ts">

    import * as d3 from "d3";

    export let from_ts: number;
    export let to_ts: number;
    export let cursorPos_ts: number | null;
    export let selectedPos_ts: number;

    $: range_ts = to_ts - from_ts;

    export let data: {
        from_ts: number,
        to_ts: number,
        count: number,
        min: number | null,
        max: number | null,
        mean: number | null
    }[] | null;

    let displaySettings = {
        showMin: true,
        showMax: true,
        showMean: true,
    }

    const width = 500;
    const height = 100;
    const margin = {top: 10, right: 30, bottom: 50, left: 30};

    let renderInfo: {
        xDomain: number[],
        xScale:  d3.ScaleLinear<number, number, never>,
        applyXAxis: (g: SVGGElement) => any,
        applyYAxis: (g: SVGGElement) => any,
        series: {
            id: string, // used to check if should rerender
            color: string,
            applyF: ((p: SVGPathElement) => any)
        }[]
    } | null = null;

    let rect: SVGRectElement;

    $: renderInfo = updateRenderInfo(displaySettings, data);

    function updateRenderInfo(displaySettings: any, data: any) {
        if (data === null) {
            renderInfo = null;
            return null;
        }
        // for the first element, from_ts is null (no lower bound)
        // for the last element, to_ts is null (no upper bound)
        let xDomain = data.map(d => d.from_ts === null ? d.to_ts : d.from_ts);
        let xScale = d3.scaleLinear()
            .domain([from_ts, to_ts])
            .range([ 0, width]);

        let seriess: { values: (number | null)[], id: string, color: string }[] = [];

        let yMins = data.map(d => d.min);
        let yMaxs = data.map(d => d.max);
        let yMeans = data.map(d => d.mean);

        if (displaySettings.showMax)
            seriess.push({
                id: "max",
                color: "gray",
                values: yMaxs,
            });
        if (displaySettings.showMean)
            seriess.push({
                id: "mean",
                color: "red",
                values: yMeans,
            });
        if (displaySettings.showMin)
            seriess.push({
                id: "min",
                color: "gray",
                values: yMins
            });

        let yMin: number | null = null;
        let yMax: number | null = null;
        let sift = function(vals: (number | null)[]) {
            for (let y of vals) {
                if (y === null) continue;
                if (yMin === null || y < yMin) yMin = y;
                if (yMax === null || y > yMax) yMax = y;
            }
        }
        for (let s of seriess) {
            sift(s.values);
        }

        if (yMin === null || yMax === null) {
            // all null
            renderInfo = null;
            return null;
        }

        let yScale = d3.scaleLinear()
            .domain([Math.min(yMin, 0.), yMax])
            .range([ height, 0]);

        function zip(x: number[], y: (number | null)[]) {
            let vals: [number, (number | null)][] = [];
            for (let i = 0; i < x.length; i++) {
                vals[i] = [x[i], y[i]];
            }
            return vals;
        }

        function createF(vals: [number, number | null][]) {
            let valsNullToZero: [number, number][] = vals.map(v => [v[0], v[1] === null ? 0 : v[1]]);

            return (p: SVGPathElement) => {
                d3.select(p)
                    .datum(valsNullToZero)
                    .attr("d", d3.line()
                        .x(d => {
                            return xScale(d[0]);
                        })
                        .y(d => yScale(d[1]))
                    )
            }
        }

        renderInfo = {
            xDomain: xDomain,
            xScale: xScale,
            applyXAxis: (g: SVGGElement) => {d3.axisBottom(xScale)(d3.select(g))},
            applyYAxis: (g: SVGGElement) => {d3.axisLeft(yScale)(d3.select(g))},
            series: seriess.map(s => { return {
                id: s.id,
                color: s.color,
                applyF: createF(zip(xDomain, s.values))
            }; })
        }

        renderInfo.applyXAxis = renderInfo.applyXAxis;
        renderInfo.applyYAxis = renderInfo.applyYAxis;
        renderInfo.series = renderInfo.series;

        return renderInfo;
    }

    function onMouseMove(ev: MouseEvent) {
        let path = ev.target as SVGPathElement;
        let bb = path.getBoundingClientRect();
        cursorPos_ts = ((ev.clientX - bb.x) / bb.width) * (to_ts - from_ts) + from_ts;
    }

    function calcCursorPos_px(from_ts: number, to_ts: number, cursorPos_ts: number) {
        return width * (cursorPos_ts - from_ts) / range_ts;
    }

</script>

<div id="container">
    <div id="controls">
        <div class="ctrl-group">
            <input id="show-min" type="checkbox" bind:checked={displaySettings.showMin} on:change={() => displaySettings = displaySettings}/>
            <label for="show-min">Show Min</label>
        </div>
        <div class="ctrl-group">
            <input id="show-mean" type="checkbox" bind:checked={displaySettings.showMean} on:change={() => displaySettings = displaySettings}/>
            <label for="show-mean">Show Mean</label>
        </div>
        <div class="ctrl-group">
            <input id="show-max" type="checkbox" bind:checked={displaySettings.showMax} on:change={() => displaySettings = displaySettings}/>
            <label for="show-max">Show Max</label>
        </div>
    </div>
    {#if renderInfo === null}
        <p style="font-style: italic">No measurements.</p>
    {:else}
        {#key renderInfo}
            <svg viewBox="0 0 {width + margin.left + margin.right} {height + margin.top + margin.bottom}">
            <g transform="translate({margin.left}, {margin.top})">
                <g use:renderInfo.applyXAxis transform="translate(0, {height})"></g>
                <g use:renderInfo.applyYAxis></g>
                {#each renderInfo.series as series (series.applyF)}
                    <path
                        fill="none"
                        stroke={series.color}
                        stroke-width="1"
                        use:series.applyF
                    ></path>
                {/each}
                <rect
                    bind:this={rect}
                    fill="none"
                    stroke="none"
                    height={height}
                    width={width}
                    pointer-events="all"
                    on:mousemove={onMouseMove}
                    on:mouseleave={() => cursorPos_ts = null}
                ></rect>
                {#if rect && cursorPos_ts !== null}
                    <rect
                    height={height}
                    width="1px"
                    opacity="1"
                    fill="black"
                    stroke="none"
                    x={calcCursorPos_px(from_ts, to_ts, cursorPos_ts)}
                    pointer-events="none"
                    ></rect>
                {/if}
                {#if rect}
                    <rect
                    height={height}
                    width="2px"
                    opacity="1"
                    fill="teal"
                    stroke="black"
                    stroke-width="1px"
                    x={calcCursorPos_px(from_ts, to_ts, selectedPos_ts)}
                    pointer-events="none"
                    ></rect>
                {/if}
            </g>
            </svg>
        {/key}
    {/if}
</div>

<style>

    #controls {
        display: flex;
    }

    .ctrl-group {
        margin-right: 1em;
    }

</style>