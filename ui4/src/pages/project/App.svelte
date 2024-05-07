<script context="module" lang="ts">
	declare var project: string;
	declare var run: string;
</script>

<script lang="ts">
    import ConfigTextEditor from "../../lib/ConfigTextEditor.svelte";
    import RunSelector from "../../lib/RunSelector.svelte";

    import { JSONEditor } from 'svelte-jsoneditor';

    let component: any = ConfigTextEditor;

</script>

<div id="app">
    <header>
        <h1>{project}</h1>
    </header>

    <main>
        <div id="pane-left">
            <h4>Config</h4>
            <ConfigTextEditor project={project}></ConfigTextEditor>
        </div>
        <div id="pane-right">
            <h4>Runs</h4>
            <RunSelector project={project}></RunSelector>
        </div>
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
        flex: 1em;
        flex-grow: 0;
        border-bottom: 2px solid teal;
    }

    header h1 {
        font-size: 1rem;
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
