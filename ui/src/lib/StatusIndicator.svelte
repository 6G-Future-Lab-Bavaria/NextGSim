<script lang="ts">

    export let status: string;

    let color = "#787878";

    let colorMap: { [key: string]: string } = {
        "RUNNING": "green",
        "STOPPED": "orange"
    };

    $: {
        if (colorMap[status])
            color = colorMap[status];
    }

</script>

<div class="status"
     style:background-color={color}
></div>

<style>
    .status {
        width: 1em;
        height: 1em;
        border-radius: 1em;
        margin: .5em;
    }
</style>