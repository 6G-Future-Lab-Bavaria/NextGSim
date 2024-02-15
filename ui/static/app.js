const F = 6;

function drawScenario(canvas, nodes, layout, network) {

    let higherCorner = layout.area["higher_corner"];
    let lowerCorner = layout.area["lower_corner"];
    canvas.width = (higherCorner["x"] - lowerCorner["x"]) * F;
    canvas.height = (higherCorner["y"] - lowerCorner["y"]) * F
    document.body.appendChild(canvas);

    let ctx = canvas.getContext("2d");
    for (let gnb of layout["gnbs"]) {
        ctx.beginPath();
        ctx.arc(gnb.x * F, gnb.y * F, 10, 0, 2*Math.PI);
        ctx.fill();
    }

    for (let ue of layout["ues"]) {
        ctx.beginPath();
        ctx.fillStyle = "blue";
        ctx.arc(ue.coords.x * F, ue.coords.y * F, 5, 0, 2*Math.PI);
        ctx.fill();
    }

    for (let link of network.links) {
        from = link["from"];
        to = link["to"];
        ctx.beginPath();
        let fromCoords = nodes[from.node].coords;
        let toCoords = nodes[to.node].coords;
        ctx.moveTo(fromCoords.x * F, fromCoords.y * F);
        ctx.lineTo(toCoords.x * F, toCoords.y * F);
        ctx.stroke();
    }
}

window.onload = async () => {

    await fetch("api/create");
    let res = await fetch("api/physical");
    let layout = await res.json();
    res = await fetch("api/network");
    let network = await res.json();

    let nodes = {}
    for (let gnb of layout["gnbs"]) { nodes[gnb.id] = gnb; }
    for (let ue of layout["ues"]) { nodes[ue.id] = ue; }

    let canvas = document.createElement("canvas");
    drawScenario(canvas, nodes, layout, network);

    await fetch("api/start");
    res = await fetch("api/events");
    let events = await res.json();

    let animations = [];

    let handle = {
        "EthernetInterface": function() {
            let lastPacketSent;
            let lastPacketFromNodeId;

            function add(ev) {

                switch (ev.type) {
                    case "packet_sent":
                        lastPacketSent = ev.time;
                        lastPacketFromNodeId = ev.component.ref.split(".")[0].slice(1);
                        break;
                    case "packet_recvd":
                        let nodeId = ev.component.ref.split(".")[0].slice(1);
                        let fromNodeCoords = nodes[lastPacketFromNodeId].coords;
                        let toNodeCoords = nodes[nodeId].coords;
                        let distX = toNodeCoords.x - fromNodeCoords.x;
                        let distY = toNodeCoords.y - fromNodeCoords.y;
                        let timeEnd = ev.time;
                        let timeStart = lastPacketSent
                        let duration = timeEnd - timeStart

                        animations.push((ctx, t) => {
                            if (t < timeStart) return;
                            if (t > timeEnd) return;
                            let relTrajPos = (t - timeStart) / duration;
                            let x = fromNodeCoords.x + relTrajPos * distX;
                            let y = fromNodeCoords.y + relTrajPos * distY;
                            ctx.beginPath();
                            ctx.fillStyle = "green";
                            ctx.arc(x * F, y * F, 5, 0, 2*Math.PI);
                            ctx.fill();
                        })
                        break;
                }

            }

            return add;
        }(),
    }

    for (let ev of events) {
        if (Object.keys(handle).includes(ev.component.name)) {
            handle[ev.component.name](ev);
        }
    }

    let minTs = 0;
    let maxTs = 2;
    let step = .05;

    window.play = async function() {
        let ctx = canvas.getContext("2d");

        function render(t) {
            return new Promise((res) => {
                window.requestAnimationFrame(() => {
                    ticker.innerText = "T = " + t.toFixed(2) + " ms";
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    drawScenario(canvas, nodes, layout, network);

                    for (let anim of animations) {
                        anim(ctx, t);
                    }
                });
                if (t < maxTs)
                    setTimeout(() => render(t + step), 500);
                else
                    res();
            });
        }

        return render(minTs);
    }

    let ticker = document.body.appendChild(document.createElement("p"));
    ticker.style.position = "absolute";
    ticker.style.left = "1em";
    ticker.style.top = "1em";
    ticker.innerText = "T = " + minTs.toFixed(2) + " ms";
    await window.play();
    document.removeChild(ticker);

}