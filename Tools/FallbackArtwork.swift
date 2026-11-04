// Generates native vector fallback artwork, including a transparent game aperture.
// Live themes use Rive; these PDFs keep controls usable when animation is disabled.
import AppKit
import CoreText

let root = URL(fileURLWithPath: CommandLine.arguments[1])
let fontURL = root.appendingPathComponent("Assets/SpaceGrotesk.ttf")
CTFontManagerRegisterFontsForURL(fontURL as CFURL, .process, nil)
func color(_ hex: UInt32) -> CGColor
{
    return CGColor(red: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
func label(_ context: CGContext, _ value: String, _ x: CGFloat, _ y: CGFloat, _ size: CGFloat = 12)
{
    context.saveGState()
    context.translateBy(x: x, y: y)
    context.scaleBy(x: 1, y: -1)
    let text = NSAttributedString(string: value, attributes: [.font: NSFont(name: "SpaceGrotesk-Regular", size: size) ?? NSFont.monospacedSystemFont(ofSize: size, weight: .regular), .foregroundColor: NSColor(cgColor: color(0xDAE5EF))!])
    let line = CTLineCreateWithAttributedString(text)
    context.textPosition = .zero
    CTLineDraw(line, context)
    context.restoreGState()
}
func circle(_ context: CGContext, _ x: CGFloat, _ y: CGFloat, _ diameter: CGFloat, _ hex: UInt32)
{
    context.setFillColor(color(hex))
    context.fillEllipse(in: CGRect(x: x-diameter/2, y: y-diameter/2, width: diameter, height: diameter))
}
func arrow(_ context: CGContext, _ x: CGFloat, _ y: CGFloat, _ direction: String, _ hex: UInt32)
{
    let turns: [String: CGFloat] = ["Up":0, "Right":1, "Down":2, "Left":3]
    context.saveGState()
    context.translateBy(x:x, y:y)
    context.rotate(by:(turns[direction] ?? 0) * .pi/2)
    context.setFillColor(color(hex))
    context.move(to:CGPoint(x:0,y:-6))
    context.addLine(to:CGPoint(x:-5.5,y:4))
    context.addLine(to:CGPoint(x:5.5,y:4))
    context.closePath()
    context.fillPath()
    context.restoreGState()
}
func generate(_ output: URL, width: CGFloat, height: CGFloat, draw: (CGContext) -> Void)
{
    var bounds = CGRect(x: 0, y: 0, width: width, height: height)
    let context = CGContext(output as CFURL, mediaBox: &bounds, nil)!
    context.beginPDFPage(nil)
    context.translateBy(x: 0, y: height)
    context.scaleBy(x: 1, y: -1)
    draw(context)
    context.endPDFPage()
    context.closePDF()
}
for name in ["Template", "NeonCircuit", "Orbit"]
{
    let project = root.appendingPathComponent(name)
    let info = try JSONSerialization.jsonObject(with: Data(contentsOf: project.appendingPathComponent("info.json"))) as! [String: Any]
    let devices = info["representations"] as! [String: Any]
    let phone = devices["iphone"] as! [String: Any]
    let representations = phone["standard"] as! [String: [String: Any]]
    for (orientation, representation) in representations
    {
        let size = representation["mappingSize"] as! [String: CGFloat]
        let w=size["width"]!, h=size["height"]!
        generate(project.appendingPathComponent("build/\(orientation).pdf"), width:w, height:h) { context in
            context.setFillColor(color(0x111B28))
            if orientation == "portrait"
            {
                context.fill(CGRect(x:0,y:0,width:w,height:h))
                label(context, name == "Orbit" ? "O R B I T / N64" : (name == "NeonCircuit" ? "NEON / CIRCUIT" : "CONTROLLER / TEMPLATE"),25,36,18)
            }
            else
            {
                // Do not paint over the emulator's screen.
                context.fill(CGRect(x:0,y:0,width:210,height:h))
                context.fill(CGRect(x:w-210,y:0,width:210,height:h))
                context.fill(CGRect(x:210,y:h-34,width:w-420,height:34))
                label(context,name == "Orbit" ? "ORBIT / N64" : "NEON / NES",25,40)
            }
            let items=representation["items"] as! [[String:Any]]
            for item in items
            {
                let f=item["frame"] as! [String:CGFloat]
                let x=f["x"]!+f["width"]!/2, y=f["y"]!+f["height"]!/2
                if item["thumbstick"] != nil
                {
                    circle(context,x,y,158,0x3B4B68)
                    circle(context,x,y,156,0x101A2D)
                    circle(context,x,y,116,0x63E8F1)
                    circle(context,x,y,114,0x080F20)
                    // The cap is a separate native thumbstick image, so it can move.
                }
                else if item["inputs"] is [String: String]
                {
                    let scale = min(f["width"]!, f["height"]!) / 132
                    context.saveGState()
                    context.translateBy(x: x, y: y)
                    context.scaleBy(x: scale, y: scale)
                    context.translateBy(x: -x, y: -y)
                    context.setFillColor(color(0x080E17))
                    context.fill(CGRect(x:x-24,y:y-62,width:48,height:124))
                    context.fill(CGRect(x:x-62,y:y-24,width:124,height:48))
                    context.setFillColor(color(0x293746))
                    context.fill(CGRect(x:x-20,y:y-58,width:40,height:116))
                    context.fill(CGRect(x:x-58,y:y-20,width:116,height:40))
                    circle(context,x,y,12,0x111B28)
                    for (direction,dx,dy) in [("Up",0.0,-40.0),("Right",40.0,0.0),("Down",0.0,40.0),("Left",-40.0,0.0)]
                    {
                        if name == "Orbit" { arrow(context,x+dx,y+dy,direction,0xB8C9DD) }
                        else { circle(context,x+dx,y+dy,4,0x8196A7) }
                    }
                    context.restoreGState()
                }
                else
                {
                    let inputs=item["inputs"] as! [String]
                    let text=inputs[0].uppercased()
                    let input=inputs[0]
                    let faces: [String: UInt32] = ["a":0x2865C5, "b":0x208556, "start":0xD94C61]
                    let isC = name == "Orbit" && input.hasPrefix("c")
                    context.setFillColor(color(name == "Orbit" ? (isC ? 0xDCB33C : faces[input, default:0x28313F]) : 0x263240))
                    context.fillPath(using:.winding) // clear any pending path
                    let bounds=CGRect(x:f["x"]!,y:f["y"]!,width:f["width"]!,height:f["height"]!)
                    context.addPath(CGPath(roundedRect:bounds,cornerWidth:bounds.height/2,cornerHeight:bounds.height/2,transform:nil))
                    context.fillPath()
                    if isC
                    {
                        arrow(context,x,y,String(input.dropFirst()),0x493500)
                    }
                    else
                    {
                        let size: CGFloat = name == "Orbit" && input == "start" ? 8 : (text.count==1 ? 18 : 9)
                        label(context,text,x-(text.count==1 ? 6 : CGFloat(text.count)*size*0.3),y+4,size)
                    }
                }
            }
        }
    }
    if name == "Orbit"
    {
        generate(project.appendingPathComponent("build/stick.pdf"), width:51, height:51) { context in
            circle(context,25.5,25.5,51,0x050B16)
            circle(context,25.5,24,46,0x455B72)
            circle(context,25.5,24,44,0x24364B)
            circle(context,25.5,24,14,0x63E8F1)
            circle(context,25.5,24,11,0x24364B)
            circle(context,25.5,24,7,0xD5FFFF)
        }
    }
}
