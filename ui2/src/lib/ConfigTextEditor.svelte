<script lang="ts">
    import {JSONEditor} from "svelte-jsoneditor";
    import {getConfig, updateConfig} from "$lib/backend";

    export let project: string;

    let props = {
        json: {},
    }

    let editor: JSONEditor;

    async function load() {
        props.json = await getConfig(project);
    }

    function changed(updatedContent, previousContent, { contentErrors, patchResult }) {
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
        <JSONEditor bind:this={editor} content={props} onChange={changed}></JSONEditor>
    </div>
{/await}

<style>
    :root {
        --jse-theme-color: rgba(26, 188, 156, 0.87);
        --jse-value-color-string: rgb(188, 26, 131);
    }

    #editor {
        height: 100%;
        width: 100%;
    }

</style>