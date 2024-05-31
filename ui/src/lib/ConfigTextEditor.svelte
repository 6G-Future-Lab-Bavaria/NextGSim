<script lang="ts">
    import {getConfig, updateConfig} from "./backend";

    import {JSONEditor, Mode} from "svelte-jsoneditor";

    export let project: string;

    let props = {
        json: {},
    }

    let editor: JSONEditor;

    async function load() {
        props.json = await getConfig(project);
    }

    function changed(updatedContent:any, previousContent:any, { contentErrors, patchResult }) {
        // content is an object { json: unknown } | { text: string }
        console.log('onChange', { updatedContent, previousContent, contentErrors, patchResult });
        let success = updateConfig(project, updatedContent.json);
        if (success)
            props = updatedContent
        else {
            console.log("Failed to update config");
        }

    }
</script>

{#await load() then _}
    <div id="editor">
        <JSONEditor bind:this={editor} mode={Mode.text} content={props} onChange={changed}></JSONEditor>
    </div>
{/await}

<style>
    :root {
        --jse-theme-color: teal;
        --jse-value-color-string: rgb(188, 26, 131);
    }

    #editor {
        min-height: 0;
        width: 100%;
        margin: 0;
        box-sizing: border-box;
    }

</style>