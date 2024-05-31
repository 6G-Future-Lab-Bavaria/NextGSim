<script lang="ts">
	import {createProject, getProjects,} from "../../lib/backend";
	import {onMount} from "svelte";

	let show = false;
	let newProject = "";

	let projects = [];

	onMount(async () => {
		projects = await getProjects();
	});

	async function createNewProject() {
		let success = await createProject(newProject);
		if (success) {
			projects = await getProjects();
			show = false;
			newProject = "";
		}
	}

</script>

<script context="module" lang="ts">
	declare var project: string;
	declare var run: string;
</script>

<main>
	<div id="panel">
		<div id="header">
			<h1>Projects</h1>
			<button class:active={show} on:click={() => show = !show}>+</button>
		</div>
		<div class="divider"></div>

		<ul id="projects">
			{#if show}
				<li>
					<input type="text" bind:value={newProject} />
					<button disabled={newProject.trim() === ""} on:click={createNewProject}>Create</button>
				</li>
			{/if}

			{#each projects as proj}
				<li><a href="/projects/{proj}">{proj}</a></li>
			{/each}

		</ul>
	</div>
</main>

<style>
	main {
		width: 100%;
		height: 100%;
		display: flex;
		flex-direction: row;
		align-items: center;
		justify-content: center;
	}

	#panel {
		width: 50%;
		height: 80%;
		background-color: teal;
		padding: 1em;
		color: white;
	}

	#header {
		width: 100%;
		display: flex;
		flex-direction: row;
		justify-content: space-between;
		align-items: baseline;
	}

	h1 {
		font-weight: bold;
		margin-top: 0;
		font-size: 1.5em;
	}

	#header button {
		display: block;
		background-color: transparent;
		border: none;
		cursor: pointer;
		color: white;
		padding: .3em;
		font-size: 2em;
		transition: transform 50ms linear;
	}

	#header button.active {
		transform: rotateZ(45deg);
	}

	.divider {
		width: 100%;
		background-color: white;
		height: 2px;
	}

	#projects {
		padding: 0;
	}

	#projects li {
		list-style: none;
		width: 100%;
		margin-bottom: .5em;
		font-size: 1.1em;
		cursor: pointer;
		display: flex;
		flex-direction: row;
	}

	#projects a, input {
		color: inherit;
		text-decoration: none;
		display: block;
		background-color: rgba(255, 255, 255, .2);
		padding: .5em;
		box-sizing: border-box;
		font-size: 1rem;
		flex: 1;
	}

	#projects input {
		border: none;
	}

	#projects button {
		display: block;
		margin-left: 1em;
		cursor: pointer;
	}

</style>
