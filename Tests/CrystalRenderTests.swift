// Rendered pixels verify effects that a successful RML compilation cannot prove.
import Foundation
import CoreGraphics
import ImageIO

struct Pixels
{
    let width: Int
    let height: Int
    let bytes: [UInt8]

    init(_ url: URL)
    {
        let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
        let image = CGImageSourceCreateImageAtIndex(source, 0, nil)!
        self.width = image.width
        self.height = image.height
        var bytes = [UInt8](repeating: 0, count: image.width * image.height * 4)
        bytes.withUnsafeMutableBytes { buffer in
            let context = CGContext(data: buffer.baseAddress, width: image.width, height: image.height,
                                    bitsPerComponent: 8, bytesPerRow: image.width * 4,
                                    space: CGColorSpaceCreateDeviceRGB(),
                                    bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue | CGBitmapInfo.byteOrder32Big.rawValue)!
            context.draw(image, in: CGRect(x:0,y:0,width:image.width,height:image.height))
        }
        self.bytes = bytes
    }

    func thumbCenter() -> CGPoint
    {
        var total = 0.0, xSum = 0.0, ySum = 0.0
        for y in 230..<335
        {
            for x in 70..<165
            {
                let index = (y * self.width + x) * 4
                if self.bytes[index] > 160 && self.bytes[index+1] > 190 && self.bytes[index+2] > 190
                {
                    total += 1
                    xSum += Double(x)
                    ySum += Double(y)
                }
            }
        }
        precondition(total > 4, "Thumb center engraving was not visible")
        return CGPoint(x:xSum/total,y:ySum/total)
    }
}

let root = URL(fileURLWithPath: CommandLine.arguments[1])
func pixels(_ name: String) -> Pixels { Pixels(root.appendingPathComponent(name + ".png")) }
let idle = pixels("idle")
let moved = pixels("moved")
let origin = idle.thumbCenter(), destination = moved.thumbCenter()
precondition(abs(destination.x-origin.x-27) < 2, "X pose did not move the visible thumb cap by 27 points")
precondition(abs(destination.y-origin.y+27) < 2, "Y pose did not move the visible thumb cap by -27 points")
precondition(pixels("tapTravel").bytes != idle.bytes, "Tap signal disappeared before reaching the display")
precondition(pixels("tapSettled").bytes == idle.bytes, "Released controller never returned to its idle artwork")
precondition(pixels("reducedEarly").bytes == pixels("reducedLate").bytes, "Reduced Motion still contains moving effects")
let landscape = pixels("landscape")
// CLI captures composite onto their preview backdrop. Compare the entire game
// opening with an unpainted point, then verify live transparency in the UI test.
let backdrop = Array(landscape.bytes[(20 * landscape.width + 300) * 4..<(20 * landscape.width + 300) * 4 + 4])
for y in 40..<346
{
    for x in 218..<626
    {
        let index = (y * landscape.width + x) * 4
        precondition(Array(landscape.bytes[index..<index+4]) == backdrop, "Artwork appears inside the landscape game aperture")
    }
}
print("Passed visible XY cap movement, complete tap pulses, idle recovery, Reduced Motion and transparent game aperture.")
