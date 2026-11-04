import UIKit
import DeltaCore
import NESDeltaCore
import N64DeltaCore

@main final class AppDelegate: UIResponder, UIApplicationDelegate
{
    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]? = nil) -> Bool
    {
        Delta.register(NES.core)
        Delta.register(N64.core)
        return true
    }

    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration
    {
        let configuration = UISceneConfiguration(name: "Controller Preview", sessionRole: connectingSceneSession.role)
        configuration.delegateClass = PreviewSceneDelegate.self
        return configuration
    }
}

final class PreviewSceneDelegate: UIResponder, UIWindowSceneDelegate
{
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions)
    {
        guard let scene = scene as? UIWindowScene else { return }
        let window = UIWindow(windowScene: scene)
        window.rootViewController = PreviewViewController()
        window.makeKeyAndVisible()
        self.window = window
    }
}

private struct TestGame: GameProtocol
{
    let fileURL: URL
    let type: GameType
}

/// A small, independently buildable preview using the production loader,
/// renderer, native controller, and NES/N64 diagnostic ROMs.
final class PreviewViewController: DeltaCore.GameViewController, GameViewControllerDelegate
{
    private var coordinator: RiveControllerSkinCoordinator?
    private var themeName = "NeonCircuit"
    private var animationsEnabled = true
    private let status = UILabel()
    private let tools = UIButton(type: .system)
    private var presses = [String: Int]()
    private var releases = [String: Int]()
    private var heldInputs = Set<String>()
    private var peakValues = [String: Double]()
    private var updateTimer: Timer?

    override func viewDidLoad()
    {
        super.viewDidLoad()
        self.delegate = self
        if ProcessInfo.processInfo.arguments.contains("--orbit") { self.themeName = "Orbit" }
        self.controllerView.playerIndex = 0
        self.controllerView.accessibilityIdentifier = "controller"
        self.controllerView.isAccessibilityElement = true
        self.controllerView.accessibilityLabel = "Game controller"
        self.coordinator = RiveControllerSkinCoordinator(controllerView: self.controllerView,
                                                        isEnabled: { [weak self] in self?.animationsEnabled == true },
                                                        fileURL: { ($0 as? DeltaCore.ControllerSkin)?.fileURL })
        self.selectTheme(self.themeName)

        self.status.textColor = .white
        self.status.font = .monospacedSystemFont(ofSize: 9, weight: .regular)
        self.status.numberOfLines = 2
        self.status.accessibilityIdentifier = "inputStatus"
        self.status.isAccessibilityElement = true
        self.view.addSubview(self.status)
        self.tools.setTitle("Themes", for: .normal)
        self.tools.accessibilityIdentifier = "themeMenu"
        self.tools.showsMenuAsPrimaryAction = true
        self.view.addSubview(self.tools)
        self.updateMenu()
        self.updateTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            MainActor.assumeIsolated { self?.updateStatus() }
        }
    }

    deinit
    {
        self.updateTimer?.invalidate()
    }

    override func viewDidLayoutSubviews()
    {
        super.viewDidLayoutSubviews()
        self.status.frame = CGRect(x: 12, y: self.view.safeAreaInsets.top, width: self.view.bounds.width-95, height: 28)
        self.tools.frame = CGRect(x: self.view.bounds.width-80, y: self.view.safeAreaInsets.top, width: 72, height: 28)
        self.coordinator?.update()
        self.view.bringSubviewToFront(self.status)
        self.view.bringSubviewToFront(self.tools)
    }

    private func selectTheme(_ name: String)
    {
        let type: GameType = name == "Orbit" ? .n64 : .nes
        if self.game?.type != type
        {
            let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            let filename = type == .n64 ? "mimi-6126231.z64" : "input-test.nes"
            let bundledROM = Bundle.main.url(forResource: filename, withExtension: nil)!
            let rom = documents.appendingPathComponent(filename)
            try! Data(contentsOf: bundledROM).write(to: rom, options: .atomic)
            self.game = TestGame(fileURL: rom, type: type)
            self.presses = [:]
            self.releases = [:]
            self.heldInputs = []
            self.peakValues = [:]
        }
        self.themeName = name
        let url = Bundle.main.url(forResource: name, withExtension: "deltaskin")!
        self.controllerView.controllerSkin = DeltaCore.ControllerSkin(fileURL: url)
        self.coordinator?.update()
        self.updateMenu()
    }

    private func updateMenu()
    {
        self.tools.menu = UIMenu(children: [
            UIAction(title: "Neon Circuit", state: self.themeName == "NeonCircuit" ? .on : .off) { [weak self] _ in self?.selectTheme("NeonCircuit") },
            UIAction(title: "Reusable Template", state: self.themeName == "Template" ? .on : .off) { [weak self] _ in self?.selectTheme("Template") },
            UIAction(title: "Orbit N64", state: self.themeName == "Orbit" ? .on : .off) { [weak self] _ in self?.selectTheme("Orbit") },
            UIAction(title: "Animate", state: self.animationsEnabled ? .on : .off) { [weak self] _ in
                guard let self else { return }
                self.animationsEnabled.toggle()
                self.coordinator?.update()
                self.updateMenu()
            },
            UIAction(title: "Run Input Demo") { [weak self] _ in
                self?.runInputDemo()
            }
        ])
    }

    private func runInputDemo()
    {
        // Exercise simultaneous controller state through the same input mapping
        // and emulator receiver as touches. Physical gestures are tested separately.
        let names = self.themeName == "Orbit" ? ["a", "b", "analogStickUp", "analogStickRight"] : ["a", "b", "up", "right"]
        let inputs = names.map {
            AnyInput(stringValue: $0, intValue: nil, type: .controller(.controllerSkin))
        }
        Task { [weak self] in
            guard let self else { return }
            for input in inputs { self.controllerView.activate(input, value: input.stringValue.hasPrefix("analog") ? 0.5 : 1) }
            try? await Task.sleep(for: .seconds(4))
            for input in inputs { self.controllerView.deactivate(input) }
        }
    }

    private func updateStatus()
    {
        let held = self.controllerView.activatedInputs.keys.map(\.stringValue).sorted().joined(separator: "+")
        let active = self.controllerView.skinRenderer == nil ? "Static" : "Rive"
        let counts = ["a", "b", "up", "right"].map { "\($0):\(self.presses[$0, default: 0])/\(self.releases[$0, default: 0])" }.joined(separator: " ")
        self.status.text = "\(active) | \(held.isEmpty ? "idle" : held)\n\(counts)"
        let allCounts = ["a", "b", "up", "down", "left", "right", "start", "select", "menu", "cUp", "cDown", "cLeft", "cRight", "l", "r", "z", "analogStickUp", "analogStickDown", "analogStickLeft", "analogStickRight"].map {
            "\($0):\(self.presses[$0, default: 0])/\(self.releases[$0, default: 0])"
        }.joined(separator: " ")
        let peaks = self.peakValues.sorted { $0.key < $1.key }.map { "\($0.key)Peak=\(String(format: "%.3f", $0.value))" }.joined(separator: " ")
        let safeFrame = self.view.safeAreaLayoutGuide.layoutFrame
        let isSafe = safeFrame.insetBy(dx: -0.5, dy: -0.5).contains(self.controllerView.frame)
        self.status.accessibilityValue = "\(allCounts) \(peaks) safeAreaContainsController=\(isSafe) safeFrame=\(safeFrame) view=\(self.view.bounds) window=\(self.view.window?.bounds ?? .zero) controller=\(self.controllerView.frame) traits=\(self.controllerView.controllerSkinTraits?.description ?? "none")"
    }

    override func gameController(_ gameController: GameController, didActivate input: Input, value: Double)
    {
        super.gameController(gameController, didActivate: input, value: value)
        self.peakValues[input.stringValue] = max(self.peakValues[input.stringValue, default: 0], value)
        if self.heldInputs.insert(input.stringValue).inserted
        {
            self.presses[input.stringValue, default: 0] += 1
        }
        self.updateStatus()
    }

    override func gameController(_ gameController: GameController, didDeactivate input: Input)
    {
        super.gameController(gameController, didDeactivate: input)
        if self.heldInputs.remove(input.stringValue) != nil
        {
            self.releases[input.stringValue, default: 0] += 1
        }
        self.updateStatus()
    }

    func gameViewController(_ gameViewController: DeltaCore.GameViewController, optionsFor game: GameProtocol) -> [EmulatorCore.Option: Any]
    {
        // Avoid the simulator's legacy OpenGL framebuffer resize failure.
        return [.metal: true]
    }
}
