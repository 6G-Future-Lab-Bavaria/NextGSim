let events = [
    {
        type: "create",
        ts: 1,
        msg: 0,
        at: 2
    },
    {
        type: "transfer",
        msg: 0,
        ts: 1,
        from: 2,
        to: 5,
    },
    {
        type: "create",
        ts: 5,
        msg: 1,
        at: 3
    },
    {
        type: "destroy",
        ts: 6,
        msg: 0,
    },
    {
        type: "transfer",
        msg: 1,
        ts: 8,
        from: 3,
        to: 5,
    },
    {
        type: "destroy",
        ts: 9,
        msg: 1,
    },
]
let entities = [
    {
        id: 2,
        x: 3,
        y: 6
    },
    {
        id: 3,
        x: 2,
        y: 9
    },
    {
        id: 5,
        x: 5,
        y: 5,
    }
]

window.test = function(x) {

}

window.onload = async () => {

    let body = document.body;

    let view = document.getElementById("view");

    let timelines = [];

    for (let entity of entities) {

        let timeline = view.appendChild(document.createElement("div"));
        timeline.classList.add("timeline");

        let overlay = timeline.appendChild(document.createElement("div"));
        overlay.classList.add("overlay");
        overlay.innerText = "Entity " + entity.id;
        let content = timeline.appendChild(document.createElement("div"));
        content.classList.add("content");

        timelines.push({
            "el": timeline,
            "ct": content,
        });
    }

    let width_per_step_em = 10;

    let minT = 0;
    let maxT = 10;

    for (let t = minT; t <= maxT; t++) {
        for (let tl of timelines) {
            let tick = document.createElement("p")
            tick.innerText = "|";
            tick.style.transform = "translateX(" + (t * width_per_step_em) + "em)";
            tl.ct.appendChild(tick);
        }
    }
}