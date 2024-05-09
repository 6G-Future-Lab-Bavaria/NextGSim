<script context="module" lang="ts">
	declare var project: string;
	declare var run: string;
</script>

<script lang="ts">
    import ConfigTextEditor from "../../lib/ConfigTextEditor.svelte";
    import RunSelector from "../../lib/RunSelector.svelte";

    import { JSONEditor } from 'svelte-jsoneditor';

    let component: any = ConfigTextEditor;

    let tabs = [{
        "name": "Config",
        "component": ConfigTextEditor,
    },
    {
        "name": "Runs",
        "component": RunSelector,
    }];

    $: tabIndex = 0;

</script>

<div id="app">
    <header>
        <div style="align-self: flex-start">
            <h1>{project}</h1>
        </div>
        <div id="tab-btns" style="align-self: flex-end">
            {#each tabs as tab, i}
                <button class:active={tabIndex === i} on:click={() => tabIndex = i}>{tab["name"]}</button>
            {/each}
        </div>
    </header>

    <main>
        <svelte:component this={tabs[tabIndex]["component"]} project={project}></svelte:component>
        <!--div id="pane-left">
            <h4>Config</h4>
            <ConfigTextEditor project={project}></ConfigTextEditor>
        </div>
        <div id="pane-right">
            <h4>Runs</h4>
            <RunSelector project={project}></RunSelector>
        </div-->
    </main>

</div>

<style>

    @import '../../global.css';

    :global(html) {
        height: 100%;
        width: 100%;
    }

    :global(body) {
        height: 100%;
        width: 100%;
        margin: 0;
        font-family: sans-serif;
    }

    #app {
        width: 100vw;
        height: 100vh;
        display: flex;
        flex-direction: column;
        color: teal;
    }

    header {
        font-size: 1.4rem;
        flex: 1em;
        flex-grow: 0;
        border-bottom: 2px solid teal;
        display: flex;
        flex-direction: row;
        align-items: baseline;
        justify-content: space-between;
    }

    #tab-btns {
        height: 100%;
        display: flex;
        flex-direction: row;
        margin-right: 1em;
    }

    #tab-btns button {
        font-size: inherit;
        background-color: transparent;
        border: none;
        cursor: pointer;
    }

    #tab-btns button.active {
        font-weight: bold;
    }

    header h1 {
        font-size: inherit;
        margin: .5em;
    }

    main {
        flex: auto;
        display: flex;
        flex-direction: row;
        min-height: 0;
    }

    main h4 {
        font-size: 1rem;
        margin: .7em;
    }

    #pane-left, #pane-right {
        display: flex;
        flex-direction: column;
    }

    #pane-left {
        flex: 3;
    }

    #pane-right {
        flex: 1;
        margin-left: 1em;
    }


</style>
