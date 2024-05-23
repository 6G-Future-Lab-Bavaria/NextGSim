<script lang="ts">

    export let visible: boolean;
    export let pos: [number, number];

    let it: HTMLDivElement;

    let boundedPos = pos;

    function calcLeft(left: number) {
        if (!it) return 0;
        let ttWidth = it.getBoundingClientRect().width;
        return Math.min(left, document.body.getBoundingClientRect().width - ttWidth);
    }

    function calcTop(top: number) {
        if (!it) return 0;
        let ttHeight = it.getBoundingClientRect().height;
        return Math.min(top, document.body.getBoundingClientRect().height - ttHeight);
    }

    $: {
        pos, visible;
        setInterval(() => {
            boundedPos = [calcLeft(pos[0]), calcTop(pos[1])];
        }, 1);
    }

</script>

<div bind:this={it} id="tooltip" style:left="{boundedPos[0]}px" style:top="{boundedPos[1]}px" style:display={visible ? "block" : "none"}>
    <slot />
</div>

<style>
    #tooltip {
        position: absolute;
        z-index: 1000;
        pointer-events: none;
    }
</style>

