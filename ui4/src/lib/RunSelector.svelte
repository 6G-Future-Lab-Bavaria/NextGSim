<script lang="ts">
    import {createRun, getRuns} from "./backend";

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
    <button on:click={newRun}>+</button>
    {#await load() then _}
        <ul id="runs">
            {#each runs as run}
            <li>
                <a href="/projects/{project}/runs/{run}">{run}</a>
            </li>
            {/each}
        </ul>
    {/await}
</div>

<style>
    button {
		display: block;
		background-color: transparent;
		border: none;
		cursor: pointer;
		color: teal;
        font-size: 1.3rem;
        font-weight: bold;
    }

    #runs {
        padding: 0;
    }

    #runs li {
        list-style: none;
    }

    #runs a {
        text-decoration: none;
        color: inherit;
        font-weight: bold;
    }

</style>
