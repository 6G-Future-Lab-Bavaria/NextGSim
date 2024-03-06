<script lang="ts">
    import {getRuns} from "$lib/backend";

    export let project: string;
</script>

<div>
    {#await getRuns(project) then runs}
        <ul>
            {#each runs as run}
            <li>
                <a href="/projects/{project}/runs/{run}">{run}</a>
            </li>
            {/each}
        </ul>
    {/await}
</div>
