
const ENDPOINT = "http://localhost:5000/projects/test1";

export async function getNetworkTopology() {
    await fetch(ENDPOINT + "/api/create");
    let res = await fetch(ENDPOINT + "/api/network");
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

export async function getEvents() {
    await fetch(ENDPOINT + "/api/create");
    await fetch(ENDPOINT + "/api/start");
    let res = await fetch(ENDPOINT + "/api/events");
    let events = await res.json();

    return events.map((ev) => {return {
        time: ev.time,
        comp: ev.component.name + "/" + ev.component.ref,
        type: ev.type,
        data: ev.data,
    }})
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