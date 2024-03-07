<script lang="ts">
    import {createRun, getRuns} from "$lib/backend";

    export let project: string;

    let runs: string[];

    async function load() {
        runs = await getRuns(project)
    }

    async function newRun() {
        await createRun(project);
        runs = await getRuns(project);
    }
</script>

<div>
    <button on:click={newRun}>New</button>
    {#await load() then _}
        <ul>
            {#each runs as run}
            <li>
                <a href="/projects/{project}/runs/{run}">{run}</a>
            </li>
            {/each}
        </ul>
    {/await}
</div>
