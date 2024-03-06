export function load({ params }) {
	return {
		project: params.proj_name,
		run: params.run,
	};
}