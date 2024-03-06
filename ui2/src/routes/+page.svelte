<script lang="ts">
    import {getProjects} from "$lib/backend";
</script>

<div id="modal">
    <div id="controls">
        <button>+</button>
    </div>
    <ul id="projects">
    {#await getProjects() then projects}
        {#each projects as proj}
        <li class="project">
            <a href="/projects/{proj}">{proj}</a>
        </li>
        {/each}
    {/await}
    </ul>
</div>

<style>
    :global(body) {
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-family: sans-serif;
    }

    #modal {
        min-height: 50%;
        max-height: 70%;
        background-color: #1abc9c;
        min-width: 40%;
        max-width: 70%;
        padding: 2em;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
    }

    #controls {
        margin-bottom: .5em;
    }

    #controls button {
        float: right;
        border: none;
        font-size: 1.5em;
        font-weight: bold;
        background: none;
        cursor: pointer;
    }

    #projects {
        list-style: none;
        padding: 0;
        margin: 0;
        width: 100%;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
        overflow-y: scroll;
        flex: 1;
    }

    .project {
        margin-bottom: 1em;
    }

    .project a {
        color: inherit;
        text-decoration: none;
        font-weight: bold;
        font-size: 1.2em;
    }
</style>