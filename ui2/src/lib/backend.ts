
const ENDPOINT = "http://localhost:5000/";

export async function getNetworkTopology(project, run) {
    await fetch(ENDPOINT + `projects/${project}/api/create`);
    let res = await fetch(ENDPOINT + `projects/${project}/api/network`);
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

export async function getMetrics(project, run) {
    await fetch(ENDPOINT + `projects/${project}/api/create`);
    await fetch(ENDPOINT + `projects/${project}/api/start`);
    let res = await fetch(ENDPOINT + `projects/${project}/api/metrics`);
    let events = await res.json();

    return events;
}

export async function getEvents(project, run) {
    await fetch(ENDPOINT + `projects/${project}/api/create`);
    await fetch(ENDPOINT + `projects/${project}/api/start`);
    let res = await fetch(ENDPOINT + `projects/${project}/api/events`);
    let events = await res.json();

    return events.map((ev) => {return {
        time: ev.time,
        comp: ev.component.name + "/" + ev.component.ref,
        type: ev.type,
        data: ev.data,
    }})
}

export async function getRunConfig(project, run) {
}

export async function getProjects() {
    let res = await fetch(ENDPOINT + "/api/projects");
    return await res.json();
}

export async function getConfig(project) {
    let res = await fetch(ENDPOINT + `projects/${project}/api/config`);
    return await res.json();
}

export async function updateConfig(project, config) {
    let res = await fetch(ENDPOINT + `projects/${project}/api/config`, {
        method: "POST",
        headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    });
    return res.status == 200;
}

export async function getRuns(project) {
    let res = await fetch(ENDPOINT + `projects/${project}/api/runs`);
    return await res.json();
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