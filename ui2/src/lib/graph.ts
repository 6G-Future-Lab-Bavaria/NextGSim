import * as d3 from "d3";

export function create() {
    let path = d3.path();
    let context = path;
    //context.moveTo(10, 10); // move current point to ⟨10,10⟩
    //context.lineTo(100, 10); // draw straight line to ⟨100,10⟩
    //context.arcTo(150, 150, 300, 10, 40); // draw an arc, the turtle ends up at ⟨194.4,108.5⟩
    //context.lineTo(300, 10);
    //context.lineTo(30,30);
    //context.moveTo(30,30);
    //context.lineTo(30,30);
    context.arc(50, 50, 20, 0, Math.PI * .3);
    //context.closePath();
    return context.toString();
}

export function createGraph() {

}