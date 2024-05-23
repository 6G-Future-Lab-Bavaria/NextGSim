<script lang="ts">
    import * as d3 from "d3";
    import BinnedTimeseriesViewer from "./BinnedTimeseriesViewer.svelte";
    import type {SvelteComponent, SvelteComponent_1} from "svelte";

    const COMPONENT_MAP: {[key: string]: ConstructorOfATypedSvelteComponent} = {
        "BinnedTimeseriesViewer": BinnedTimeseriesViewer
    };

    // todo: fix type change
    // todo: fix live updates (only updated when destroyed)

    export let metrics: {
        comp: string,
        name: string,
        ui_comp: string,
        data: any,
    }[];

    export let from_ts: number;
    export let to_ts: number;
    export let cursorPos_ts: number | null;

    let type = "line";

    let cursors: SVGRectElement[] = [];

    function render(svgEl: SVGElement, values: [number, number][]) {
        if (values.length == 0) return {}

        const width = 500;
        const height = 100;
        const margin = {top: 10, right: 30, bottom: 50, left: 30};

        svgEl.innerHTML = "";

        let svg = d3.select(svgEl)
            //.attr("width", width + margin.left + margin.right)
            //.attr("height", height + margin.top + margin.bottom)
            .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
            .append("g")
            .attr("transform",
                  "translate(" + margin.left + "," + margin.top + ")");

        let xvals = [];
        let yvals = [];
        for (let [x,y] of values) {
            xvals.push(x);
            yvals.push(y);
        }

        console.log("domain", [Math.min(...xvals), Math.max(...xvals)])

        let x = d3.scaleLinear()
            .domain([Math.min(...xvals), Math.max(...xvals)])
            .range([ 0, width]);
        let y = d3.scaleLinear()
            .domain([Math.min(...yvals), Math.max(...yvals)])
            .range([ height, 0]);
        svg.append("g")
            .call(d3.axisBottom(x))
            .attr("transform", `translate(0,${height})`);
        svg.append("g").call(d3.axisLeft(y));

        if (type == "scatter") {
            svg.append('g')
            .selectAll("dot")
            .data(values)
            .enter()
            .append("circle")
              .attr("cx", function (d) { return x(d[0]); } )
              .attr("cy", function (d) { return y(d[1]); } )
              .attr("r", 3)
              .style("fill", "red");
        } else if (type == "line") {
            svg.append("path")
                .datum(values)
                .attr("fill", "none")
                .attr("stroke", "red")
                .attr("stroke-width", 2)
                .attr("d", d3.line()
                .x(function(d) { return x(d[0]) })
                .y(function(d) { return y(d[1]) })
                );
        }

        let rect = svg.append("rect")
            .attr("fill", "none")
            .attr("stroke", "none")
            .attr("height", height)
            .attr("width", width)
            .attr("pointer-events", "all")
            .on("mousemove", (ev: MouseEvent) => {
                // @ts-ignore
                let path: SVGPathElement = ev.target;
                let bb = path.getBoundingClientRect();
                cursorPos_ts = ((ev.clientX - bb.x) / bb.width) * (to_ts - from_ts) + from_ts;
            })
            .on("mouseleave", (ev: MouseEvent) => {
                cursorPos_ts = null;
            });

        let cursor = svg.append("rect")
            .attr("fill", "black")
            .attr("stroke", "none")
            .attr("height", height)
            .attr("width", "2px")
            .attr("display", "none");

        //if (!cursors.includes(cursor.node()!!))
        //    cursors.push(cursor.node()!!);
    }

    /*$: {
        cursorPos_ts;
        if (cursorPos_ts === null)
            for (let c of cursors) {

                c.attr("display", "none");
            }
        else {
            cursor.attr("left", )
        }
    }*/

    function action(svgEl: SVGElement, values: [number, number][]) {
        render(svgEl, values);

        return {
            update(values: [number, number][]) {
                render(svgEl, values);
            }
        }
    }

</script>


<div id="controls">
</div>

<div id="metrics">
        {#each metrics as metric}
        <!--div-- class="metric">
            <div class="metric-id">{metric.comp}#{metric.name}</div>
            {#if metric.values.length > 0}
                <div class="metric-values">
                <svg class="metric-svg" use:action={metric.values}>



                </svg>
            </div>
            {:else}
            <p>No measurements</p>
            {/if}
        </div-->
            <div class="metric">
                <div class="metric-id">{metric.comp}#{metric.name}</div>
                <div class="metric-container">
                    {#if COMPONENT_MAP[metric.ui_comp] !== undefined}
                        <svelte:component
                                this={COMPONENT_MAP[metric.ui_comp]}
                                data={metric.data}
                                from_ts={from_ts}
                                to_ts={to_ts}
                                bind:cursorPos_ts={cursorPos_ts}
                        ></svelte:component>
                    {:else}
                        <p style="font-style: italic">Cannot render '{metric.ui_comp}'</p>
                    {/if}
                </div>
            </div>
        {/each}
        {#if metrics.length === 0}
            <p style="font-style: italic">No metrics available</p>
        {/if}
    </div>

<style>
    #controls {
        padding: 1em;
    }

    #metrics {
        min-height: 0;
        overflow-y: scroll;
    }

    .metric {
        margin-bottom: 1em;
        width: 100%;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: left;
    }

    .metric-id {
        margin-right: 1em;
        font-weight: bold;
    }

    .metric-container {
        width: 100%;
    }

    .metric-values {
        flex: auto;
        padding: 1em;
    }

    .metric-svg {
    }
</style>