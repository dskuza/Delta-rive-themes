import Foundation
import ZIPFoundation

@main struct ManifestTests
{
    static func main() throws
    {
        let root = URL(fileURLWithPath: CommandLine.arguments[1])
        let fixture = try Data(contentsOf: root.appendingPathComponent("Template/rive.json"))
        let manifest = try RiveControllerSkinManifest(data: fixture)
        let representation = manifest.representations["iphone-standard-portrait"]!
        precondition(representation.sticks == nil)
        let stick = try JSONDecoder().decode(RiveControllerSkinManifest.Stick.self, from: Data("""
        {"up":"up","down":"down","left":"left","right":"right","x":"stickX","y":"stickY"}
        """.utf8))
        precondition(stick.axes(for: [:]) == (0, 0))
        precondition(stick.axes(for: ["right": 0.75, "up": 0.5]) == (0.75, 0.5))
        precondition(stick.axes(for: ["left": 1, "down": 1]) == (-1, -1))
        precondition(stick.axes(for: ["left": 1, "right": 1]) == (0, 0))
        precondition(stick.axes(for: ["right": .nan, "up": .infinity]) == (0, 0))
        precondition(stick.axes(for: ["right": 3, "down": -2]) == (1, 0))
        precondition(stick.magnitude == nil)
        precondition(stick.contact == nil)
        precondition(stick.magnitude(for: [:]) == 0)
        precondition(stick.magnitude(for: ["right": 0.3, "up": 0.4]) == 0.5)
        precondition(stick.magnitude(for: ["left": 1, "down": 1]) == 1)
        precondition(stick.magnitude(for: ["right": .nan, "up": .infinity]) == 0)

        let analogFixture = Data("""
        {"schemaVersion":1,"representations":{"iphone-standard-portrait":{
          "file":"Orbit.riv","artboard":"Portrait","stateMachine":"Controller","viewModel":"Controller","buttons":{},
          "sticks":[{"up":"analogStickUp","down":"analogStickDown","left":"analogStickLeft","right":"analogStickRight",
                     "x":"stickX","y":"stickY","active":"stickActive","magnitude":"stickMagnitude","contact":"stickContact"}]
        }}}
        """.utf8)
        let analog = try RiveControllerSkinManifest(data: analogFixture)
        precondition(analog.representations["iphone-standard-portrait"]!.numberPaths == ["stickX", "stickY", "stickMagnitude"])
        precondition(analog.representations["iphone-standard-portrait"]!.booleanPaths == ["stickActive", "stickContact"])

        func rejects(_ data: Data) throws
        {
            do
            {
                _ = try RiveControllerSkinManifest(data: data)
                fatalError("Invalid manifest was accepted")
            }
            catch is RiveControllerSkinManifest.Error {}
        }
        try rejects(Data(String(data: fixture, encoding: .utf8)!.replacingOccurrences(of: "\"schemaVersion\": 1", with: "\"schemaVersion\": 2").utf8))
        try rejects(Data(String(data: fixture, encoding: .utf8)!.replacingOccurrences(of: "Template.riv", with: "../Template.riv").utf8))
        try rejects(Data(String(data: fixture, encoding: .utf8)!.replacingOccurrences(of: "\"aPressed\"", with: "\"bPressed\"").utf8))
        try rejects(Data(String(data: fixture, encoding: .utf8)!.replacingOccurrences(of: "\"aPressed\"", with: "\"a//pressed\"").utf8))
        try rejects(Data(String(data: analogFixture, encoding: .utf8)!.replacingOccurrences(of: "\"magnitude\":\"stickMagnitude\"", with: "\"magnitude\":\"stickX\"").utf8))
        try rejects(Data(String(data: analogFixture, encoding: .utf8)!.replacingOccurrences(of: "\"contact\":\"stickContact\"", with: "\"contact\":\"stickActive\"").utf8))

        let temporary = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: temporary, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: temporary) }
        func archive(_ name: String, members: [String: Data]) throws -> URL
        {
            let url = temporary.appendingPathComponent(name)
            let archive = try Archive(url: url, accessMode: .create)
            for (path, data) in members
            {
                try archive.addEntry(with: path, type: .file, uncompressedSize: Int64(data.count)) { position, size in
                    data.subdata(in: Int(position)..<Int(position) + size)
                }
            }
            return url
        }
        let legacy = try archive("legacy.deltaskin", members: ["info.json": Data("{}".utf8)])
        try RiveControllerSkinArchive.validate(at: legacy)
        let legacyAsset = try RiveControllerSkinArchive.load(at: legacy, traits: "iphone-standard-portrait")
        precondition(legacyAsset == nil)
        let missing = try archive("missing.deltaskin", members: ["rive.json": fixture])
        do
        {
            try RiveControllerSkinArchive.validate(at: missing)
            fatalError("Missing Rive asset was accepted")
        }
        catch is RiveControllerSkinManifest.Error {}
        let corrupt = try archive("corrupt.deltaskin", members: ["rive.json": fixture, "Template.riv": Data("BAD!".utf8)])
        do
        {
            try RiveControllerSkinArchive.validate(at: corrupt)
            fatalError("Invalid Rive header was accepted")
        }
        catch is RiveControllerSkinManifest.Error {}
        let oversized = try archive("oversized.deltaskin", members: ["rive.json": Data(repeating: 0, count: 256 * 1024 + 1)])
        do
        {
            try RiveControllerSkinArchive.validate(at: oversized)
            fatalError("Oversized manifest was accepted")
        }
        catch is RiveControllerSkinManifest.Error {}

        for name in ["Template", "NeonCircuit", "Orbit", "OrbitCrystal"]
        {
            let url = root.appendingPathComponent("Dist/\(name).deltaskin")
            try RiveControllerSkinArchive.validate(at: url)
            for traits in manifest.representations.keys
            {
                let asset = try RiveControllerSkinArchive.load(at: url, traits: traits)
                precondition(asset != nil)
            }
            let unsupported = try RiveControllerSkinArchive.load(at: url, traits: "tv-standard-landscape")
            precondition(unsupported == nil)
        }
        let orbit = try RiveControllerSkinArchive.load(at: root.appendingPathComponent("Dist/Orbit.deltaskin"), traits: "iphone-standard-portrait")!
        let orbitStick = orbit.representation.sticks!.first!
        precondition(orbitStick.axes(for: ["analogStickRight":0.25,"analogStickDown":0.5,"right":1]) == (0.25,-0.5))
        precondition(orbitStick.magnitude == "stickMagnitude")
        let crystal = try RiveControllerSkinArchive.load(at: root.appendingPathComponent("Dist/OrbitCrystal.deltaskin"), traits: "iphone-edgeToEdge-landscape")!
        precondition(crystal.representation.sticks!.first!.contact == "stickContact")
        print("Passed manifest validation, archive compatibility, malformed assets, and normalized stick input tests.")
    }
}
