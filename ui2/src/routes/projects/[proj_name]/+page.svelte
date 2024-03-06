<script lang="ts">
    import ConfigTextEditor from "$lib/ConfigTextEditor.svelte";
    import RunSelector from "$lib/RunSelector.svelte";

    export let data;
    let project = data.project;

    let component: any = ConfigTextEditor;

</script>

<div id="app">

    <aside id="sidebar">
        <ul>
            <li on:click={() => component = ConfigTextEditor}>TE</li>
            <li on:click={() => component = RunSelector}>RUN</li>
        </ul>
    </aside>

    <main id="main">
        <svelte:component this={component} project={project}></svelte:component>
    </main>

</div>

<style>

    :global(body) {
        height: 100%;
        width: 100%;
        margin: 0;
        font-family: sans-serif;
    }

    #app {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: row;
    }

    #sidebar {
        flex: 5%;
        padding: 1em;
        box-sizing: border-box;
        background-color: rgba(26, 188, 156, 0.2);
    }

    #sidebar ul {
        list-style: none;
        padding: 0;
        margin: 0;
        font-weight: bold;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    #sidebar li {
        margin-bottom: 1em;
        cursor: pointer;
    }

    #main {
        flex: 95%;
        background-color: rgba(26, 188, 156, 0.35);
    }

</style>
