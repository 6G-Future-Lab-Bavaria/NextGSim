<script lang="ts">
    import {getNetworkTopology} from "$lib/backend";
    import {create} from "$lib/graph";
    import * as d3 from "d3";
    import {onMount} from "svelte";

    export let project: string;

    let svg;
    $: currentNode = "";
    $: modalDisplay = "none";
    $: modalTransform = "";

    onMount(async () => {

        let s = 10
        d3.select(svg).append("defs").append("marker")
        .attr("id", "triangle")
        .attr("refX", 8)
        .attr("refY", s/2)
        .attr('viewBox', [0, 0, s, s])
        .attr("markerWidth", s)
        .attr("markerHeight", s)
        .attr("orient", "auto-start-reverse")
        .append("path")
        .attr("d", d3.line()([[0, 0], [0, s], [s, s/2]]))
        .style("fill", "black");

        let top = await getNetworkTopology(project);
        let nodes = top.nodes;
        let links = top.links;

        let link = d3.select(svg).selectAll("line")
                .data(links).join("line")
                    .style("stroke", "#aaa")
                    .style("stroke-width", ".1em")
                    .attr("marker-end", "url(#triangle)");

            let node = d3.select(svg).selectAll("circle")
                .data(nodes).join("circle")
                    .style("fill", "blue")
                    .attr("r", 10);

        //@ts-ignore
    let simulation = d3.forceSimulation(nodes)
    //@ts-ignore
    .force("link", d3.forceLink().id((d) => d.id).links(links).distance(() => 100))
    .force("charge", d3.forceManyBody().strength(-80))
    .force("center", d3.forceCenter(500, 300))
        .on("tick", () => {
            //console.log("sim done");
            //console.log(nodes);

            link
                .each(function(this: SVGLineElement, d) {
                    let dir = [d.target.x - d.source.x, d.target.y - d.source.y];
                    this.setAttribute("x1", d.source.x + dir[0]*.4);
                    this.setAttribute("y1", d.source.y + dir[1]*.4);
                    this.setAttribute("x2", d.source.x + dir[0]*.8);
                    this.setAttribute("y2", d.source.y + dir[1]*.8);
                })

            node
                 .attr("cx", function (d: any) { return d.x; })
                 .attr("cy", function(d: any) { return d.y; })
                .on("click", function(ev: MouseEvent, d) {
                   modalDisplay = "block";
                   let x = ev.clientX;
                   let y = ev.clientY;
                   modalTransform = "translate(" + x + "px, " + y + "px)";
                   currentNode = d.id;
                   ev.stopPropagation();
                });

            node.on("hover")
        });
    });

    let bodyOnClick = (ev) => {
        modalDisplay = "none";
    };

</script>

<svelte:body on:click={bodyOnClick}></svelte:body>

<div id="modal" style:display="{modalDisplay}" style:transform="{modalTransform}">
    Node #{currentNode}
</div>

<svg bind:this={svg} width = "1000px" height = "600px">
</svg>

<style>
    #modal {
        position: absolute;
        height: 2em;
        width: 4em;
        left: 0;
        top: 0;
        border: 3px solid black;
        background: lightgoldenrodyellow;
    }

</style>