<script lang="ts">
    import * as d3 from "d3";

    import {getMetrics} from "$lib/backend";

    export let project: string;

    let metrics: any[];

    let type = "line";

    async function load() {
        metrics = [];
        let ms = await getMetrics(project);

        for (let m of ms) {
            let values = m.values;

            let width = 500;
            let height = 100;
            let margin = {top: 10, right: 30, bottom: 30, left: 60};

            let render = function(svgEl: SVGElement) {
                let svg = d3.select(svgEl)
                    .attr("width", width + margin.left + margin.right)
                    .attr("height", height + margin.top + margin.bottom)
                    .append("g")
                    .attr("transform",
                          "translate(" + margin.left + "," + margin.top + ")");

                let xvals = [];
                let yvals = [];
                for (let [x,y] of values) {
                    xvals.push(x);
                    yvals.push(y);
                }

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
            }

            if (values.length == 0)
                render = () => {};

            metrics.push({
                comp: m.comp,
                name: m.name,
                values: m.values,
                render: render,
            });
        }

        metrics = metrics;
    }

</script>


<div id="controls">
    <span>Type: </span>
    <select bind:value={type} on:change={load}>
        <option value="line">line</option>
        <option value="scatter">scatter</option>
    </select>
</div>

{#await load() then _}
    <div id="metrics">
        {#each metrics as metric}
        <div class="metric">
            <div class="metric-id">{metric.comp}#{metric.name}</div>
            {#if metric.values.length > 0}
                <div class="metric-values">
                <svg class="metric-svg" use:metric.render></svg>
            </div>
                {:else}
                <p>No measurements</p>
                {/if}
        </div>
        {/each}
    </div>
{/await}

<style>
    #controls {
        padding: 1em;
    }

    .metric {
        margin-bottom: 1em;
        width: 100%;
        padding: 1em;
        box-sizing: border-box;
        display: flex;
        flex-direction: row;
        align-items: center;
    }

    .metric-id {
        margin-right: 1em;
        font-weight: bold;
    }

    .metric-svg {
        width: 100%;
        margin: 1em;
    }
</style>