
const ENDPOINT = "";

export async function getNetworkTopology(project: string, run: string) {
    let res = await fetch(ENDPOINT + `projects/${project}/api/runs/${run}/events`);
    let top = await res.json();

    let nodes: [any] = top.nodes;
    for (let node of nodes) {
        node.inLinks = [];
        node.outLinks = [];
    }

    let links = [];
    for (let l of top.links) {
        let fromNode = nodes.find((n) => n.id == l.from.node);
        let toNode = nodes.find((n) => n.id == l.from.node);
        fromNode.outLinks.push(l);
        toNode.inLinks.push(l);
        links.push({
            source: l.from.node,
            target: l.to.node,
            ifs: [l.from.if, l.to.if],
        });
    }
    console.log(nodes)
    return {
        nodes: nodes,
        links: links,
    }

    /*const nodes = [
            {
                id: 0,
                name: "test",
            },
            {
                id: 1,
                name: "test",
            },
            {
                id: 2,
                name: "test",
            },
        ];
    return {
        nodes: nodes,
        links: [
            { "source": 0, "target": 1 },
            { "source": 1, "target": 0 },
            { "source": 1, "target": 2 },
        ]
    }*/
}

export async function getMetrics(project: string, run: string, from: number, to: number, args: { [id: string] : any; }) {
    let params = Object.entries(args).map(([k,v]) => `${k}=${v}`).join("&");
    let res = await fetch(ENDPOINT + `/api/projects/${project}/runs/${run}/metrics?from=${from}&to=${to}&${params}`);
    let metrics = await res.json();
    return metrics;
}

export async function getEvents(project: string, run: string, from: number, to: number, args: { [id: string] : any; }) {
    let params = Object.entries(args).map(([k,v]) => `${k}=${v}`).join("&");
    let res = await fetch(ENDPOINT + `/api/projects/${project}/runs/${run}/events?from=${from}&to=${to}&${params}`);
    let events = await res.json();
    return events;
}

export async function getTopologyAtTime(project: string, run: string, ts: number, args: { [id: string] : any; }) {
    let params = Object.entries(args).map(([k,v]) => `${k}=${v}`).join("&");
    let res = await fetch(ENDPOINT + `/api/projects/${project}/runs/${run}/topology?time=${ts}&${params}`);
    let tops = await res.json();
    return tops;
}

export async function getRunConfig(project: string, run: string) {
    let res = await fetch(ENDPOINT + `/api/projects/${project}/runs/${run}/config`);
    return await res.json();
}

export async function getProjects() {
    let res = await fetch(ENDPOINT + "/api/projects");
    return await res.json();
}

export async function getConfig(project) {
    let res = await fetch(ENDPOINT + `/api/projects/${project}/config`);
    return await res.json();
}

export async function updateConfig(project, config) {
    let res = await fetch(ENDPOINT + `/api/projects/${project}/config`, {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    });
    return res.status == 200;
}

export async function getRuns(project) {
    let res = await fetch(ENDPOINT + `/api/projects/${project}/runs`);
    return await res.json();
}

export async function startRun(project, run) {
    await fetch(ENDPOINT + `/api/projects/${project}/runs/${run}/start`, {method: "POST"});
}

export async function stopRun(project, run) {
    await fetch(ENDPOINT + `/api/projects/${project}/runs/${run}/stop`, {method: "POST"});
}

export async function getRun(project: string, run: string): Promise<{config: any, status: string, duration_ts: number}> {
    let res = await fetch(ENDPOINT + `/api/projects/${project}/runs/${run}`, { method: "GET" });
    return await res.json();
}

export async function loadRun(project, run) {
    let res = await fetch(ENDPOINT + `/api/projects/${project}/runs/${run}/load`, { method: "POST" });
    return await res.text();
}

export async function createRun(project: string) {
    let res = await fetch(ENDPOINT + `/api/projects/${project}/runs`, { method: "POST" });
    return await res.text();
}

export async function createProject(name: string) {
    let res = await fetch(ENDPOINT + `/api/projects/${name}`, { method: "POST" })
    return res.status == 200;
}

export function getMECTopology() {
    return {
        entities: [
            {
                id: 0,
                services: [ "Service1", "Service2" ]
            },
            {
                id: 2,
                services: [ "Service3" ]
            },
        ]
    }
}