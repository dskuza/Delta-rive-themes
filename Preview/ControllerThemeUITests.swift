import XCTest

final class ControllerThemeUITests: XCTestCase
{
    override func setUp()
    {
        self.continueAfterFailure = false
        XCUIDevice.shared.orientation = .portrait
    }

    func testNativeButtonsDPadAndThemeLifecycle()
    {
        let app = XCUIApplication()
        app.launch()
        let status = app.staticTexts["inputStatus"]
        XCTAssertTrue(status.waitForExistence(timeout: 20))
        self.waitForText("Rive | idle", in: status)
        let controller = app.descendants(matching: .any)["controller"]
        XCTAssertTrue(controller.exists, app.debugDescription)

        self.point(326, 141, width: 390, height: 330, in: controller).press(forDuration: 0.2)
        self.waitForText("a:1/1", in: status)
        self.point(253, 178, width: 390, height: 330, in: controller).press(forDuration: 0.2)
        self.waitForText("b:1/1", in: status)

        let center = self.point(100, 158, width: 390, height: 330, in: controller)
        let diagonal = self.point(152, 106, width: 390, height: 330, in: controller)
        center.press(forDuration: 0.1, thenDragTo: diagonal, withVelocity: .slow, thenHoldForDuration: 0.2)
        self.waitForText("Rive | idle", in: status)
        XCTAssertFalse(status.label.contains("up:0/0"))
        XCTAssertFalse(status.label.contains("right:0/0"))

        app.buttons["themeMenu"].tap()
        app.buttons["Animate"].tap()
        self.waitForText("Static | idle", in: status)
        self.point(326, 141, width: 390, height: 330, in: controller).tap()
        self.waitForText("a:2/2", in: status)
        app.buttons["themeMenu"].tap()
        app.buttons["Animate"].tap()
        self.waitForText("Rive | idle", in: status)

        app.buttons["themeMenu"].tap()
        app.buttons["Reusable Template"].tap()
        self.waitForText("Rive | idle", in: status)
        XCUIDevice.shared.orientation = .landscapeLeft
        self.waitForText("Rive | idle", in: status)
        print("After rotation: \(status.value ?? "")")
        self.point(763, 173, width: 844, height: 390, in: controller).tap()
        self.waitForText("a:3/3", in: status)
        XCUIDevice.shared.press(.home)
        app.activate()
        self.waitForText("Rive | idle", in: status)
        let landscape = XCTNSPredicateExpectation(predicate: NSPredicate { _, _ in abs(controller.frame.width / controller.frame.height - 844.0 / 390.0) < 0.02 }, object: nil)
        XCTAssertEqual(XCTWaiter.wait(for: [landscape], timeout: 10), .completed)
        print("After resume: \(status.value ?? "")")
        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        attachment.name = "NES diagnostic with Rive controller"
        attachment.lifetime = .keepAlways
        self.add(attachment)
    }

    func testSimultaneousInputs()
    {
        let app = XCUIApplication()
        app.launch()
        let status = app.staticTexts["inputStatus"]
        XCTAssertTrue(status.waitForExistence(timeout: 20))
        self.waitForText("Rive | idle", in: status)
        app.buttons["themeMenu"].tap()
        app.buttons["Run Input Demo"].tap()
        self.waitForText("a+b+right+up", in: status)
        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        attachment.name = "Simultaneous A B and diagonal inputs"
        attachment.lifetime = .keepAlways
        self.add(attachment)
        self.waitForText("Rive | idle", in: status)
        self.waitForText("a:1/1", in: status)
        self.waitForText("b:1/1", in: status)
    }

    func testEveryNESControl()
    {
        let app = XCUIApplication()
        app.launch()
        let status = app.staticTexts["inputStatus"]
        XCTAssertTrue(status.waitForExistence(timeout: 20))
        self.waitForText("Rive | idle", in: status)
        let controller = app.descendants(matching: .any)["controller"]
        let controls: [(String, CGFloat, CGFloat)] = [
            ("up", 100, 118), ("down", 100, 198), ("left", 60, 158), ("right", 140, 158),
            ("a", 326, 141), ("b", 253, 178), ("select", 153, 265), ("start", 233, 265), ("menu", 40, 292)
        ]
        for (name, x, y) in controls
        {
            self.point(x, y, width: 390, height: 330, in: controller).tap()
            let expectation = XCTNSPredicateExpectation(predicate: NSPredicate(format: "value CONTAINS %@", "\(name):1/1"), object: status)
            XCTAssertEqual(XCTWaiter.wait(for: [expectation], timeout: 10), .completed, name)
        }
        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        attachment.name = "Every NES control pressed and released"
        attachment.lifetime = .keepAlways
        self.add(attachment)
    }

    func testOrbitAnalogAndControls()
    {
        self.checkN64Theme(argument: "--orbit")
    }

    func testCrystalNESControlsAndSafeAreas()
    {
        let app = XCUIApplication()
        app.launchArguments = ["--crystal-nes"]
        app.launch()
        let status = app.staticTexts["inputStatus"]
        XCTAssertTrue(status.waitForExistence(timeout: 30))
        self.waitForText("Rive | idle", in: status)
        self.waitForValue("safeAreaContainsController=true", in: status)
        let controller = app.descendants(matching: .any)["controller"]
        let controls: [(String,CGFloat,CGFloat)] = [
            ("up",101,97), ("down",101,184), ("left",57,141), ("right",144,141),
            ("b",243,137), ("a",329,137), ("select",155,257), ("start",235,257), ("menu",352,65)
        ]
        for (name,x,y) in controls
        {
            self.point(x,y,width:390,height:292,in:controller).tap()
            self.waitForValue("\(name):1/1", in: status)
        }
        // The NES cross must produce digital diagonals and release both directions.
        self.point(101,141,width:390,height:292,in:controller).press(forDuration:0.1,
            thenDragTo:self.point(141,101,width:390,height:292,in:controller),
            withVelocity:.slow,thenHoldForDuration:0.2)
        self.waitForValue("up:2/2", in: status)
        self.waitForValue("right:2/2", in: status)
        self.waitForText("Rive | idle", in: status)
        app.buttons["themeMenu"].tap()
        app.buttons["Animate"].tap()
        self.waitForText("Static | idle", in: status)
        self.point(329,137,width:390,height:292,in:controller).tap()
        self.waitForValue("a:2/2", in: status)
        app.buttons["themeMenu"].tap()
        app.buttons["Animate"].tap()
        self.waitForText("Rive | idle", in: status)
        for (index,orientation) in [UIDeviceOrientation.landscapeLeft,.landscapeRight].enumerated()
        {
            XCUIDevice.shared.orientation = orientation
            self.waitForValue("traits=iphone-edgeToEdge-landscape", in: status)
            self.waitForValue("safeAreaContainsController=true", in: status)
            for (name,x,y,count) in [("a",774.0,268.0,index+3),("b",707.0,336.0,index+2),
                                     ("select",374.0,361.0,index+2),("start",470.0,361.0,index+2),
                                     ("menu",423.0,29.0,index+2)]
            {
                self.point(x,y,width:844,height:390,in:controller).tap()
                self.waitForValue("\(name):\(count)/\(count)", in: status)
            }
            let shot = XCTAttachment(screenshot:XCUIScreen.main.screenshot())
            shot.name = "Crystal NES safe area \(orientation.rawValue)"
            shot.lifetime = .keepAlways
            self.add(shot)
        }
        XCUIDevice.shared.press(.home)
        app.activate()
        self.waitForText("Rive | idle", in: status)
        app.buttons["themeMenu"].tap()
        app.buttons["Run Input Demo"].tap()
        self.waitForText("a+b+right+up", in: status)
        let active = XCTAttachment(screenshot:XCUIScreen.main.screenshot())
        active.name = "Crystal NES simultaneous buttons and circuit signals"
        active.lifetime = .keepAlways
        self.add(active)
        self.waitForText("Rive | idle", in: status)
    }

    func testCrystalAnalogContactAndControls()
    {
        self.checkN64Theme(argument: "--crystal")
    }

    private func checkN64Theme(argument: String)
    {
        let app = XCUIApplication()
        app.launchArguments = [argument]
        app.launch()
        let status = app.staticTexts["inputStatus"]
        XCTAssertTrue(status.waitForExistence(timeout: 30))
        self.waitForText("Rive | idle", in: status)
        self.waitForValue("safeAreaContainsController=true", in: status)
        let controller = app.descendants(matching: .any)["controller"]
        let crystal = argument == "--crystal"
        let stickX: CGFloat = crystal ? 91 : 116
        let stickY: CGFloat = crystal ? 137 : 284
        let center = self.point(stickX,stickY,width:390,height:400,in:controller)
        if argument == "--crystal"
        {
            // A resting thumb wakes the socket without introducing any analog input.
            center.press(forDuration: 1)
            self.waitForValue("neutralContactObserved=true", in: status)
            self.waitForValue("contact=false", in: status)
            self.waitForText("Rive | idle", in: status)
            XCTAssertFalse((status.value as? String ?? "").contains("analogStickRightPeak="))
            XCTAssertFalse((status.value as? String ?? "").contains("analogStickUpPeak="))
        }
        // A small physical drag must stay analog, rather than jumping to 1.
        center.press(forDuration: 0.1,
                     thenDragTo: self.point(stickX+8, stickY-8, width: 390, height: 400, in: controller),
                     withVelocity: .slow, thenHoldForDuration: 0.2)
        self.waitForText("Rive | idle", in: status)
        let values = (status.value as? String ?? "").split(separator: " ")
        for axis in ["analogStickRight", "analogStickUp"]
        {
            let peak = values.first { $0.hasPrefix(axis + "Peak=") }?.split(separator: "=").last.flatMap { Double($0) }
            XCTAssertNotNil(peak, status.value as? String ?? "")
            XCTAssertGreaterThan(peak ?? 0, 0.1)
            XCTAssertLessThan(peak ?? 1, 0.7)
        }
        center.press(forDuration: 0.1,
                     thenDragTo: self.point(stickX-41, stickY+41, width: 390, height: 400, in: controller),
                     withVelocity: .slow, thenHoldForDuration: 0.2)
        self.waitForText("Rive | idle", in: status)
        for axis in ["analogStickLeft", "analogStickDown"]
        {
            XCTAssertTrue((status.value as? String ?? "").contains(axis + "Peak=1.000"), status.value as? String ?? "")
        }

        let controls: [(String, CGFloat, CGFloat)] = crystal ? [
            ("up",94,268), ("down",94,354), ("left",51,311), ("right",137,311),
            ("a",335,183), ("b",243,154), ("cUp",288,266), ("cDown",288,362),
            ("cLeft",241,313), ("cRight",336,314), ("l",58,55), ("r",332,55),
            ("z",332,18), ("start",195,238), ("menu",194,52)
        ] : [
            ("up",78,113), ("down",78,165), ("left",52,139), ("right",104,139),
            ("a",267,258), ("b",227,206), ("cUp",317,121), ("cDown",317,179),
            ("cLeft",288,150), ("cRight",346,150), ("l",44,78), ("r",346,78),
            ("z",argument == "--crystal" ? 346 : 116,argument == "--crystal" ? 42 : 378),
            ("start",195,141),
            ("menu",argument == "--crystal" ? 195 : 40,argument == "--crystal" ? 108 : 378)
        ]
        for (name, x, y) in controls
        {
            self.point(x,y,width:390,height:400,in:controller).tap()
            XCTAssertTrue((status.value as? String ?? "").contains("\(name):1/1"), name)
        }
        if argument == "--crystal"
        {
            self.point(58,18,width:390,height:400,in:controller).tap()
            self.waitForValue("z:2/2", in: status)
        }

        app.buttons["themeMenu"].tap()
        app.buttons["Animate"].tap()
        self.waitForText("Static | idle", in: status)
        self.waitForValue("safeAreaContainsController=true", in: status)
        center.press(forDuration: 0.1,
                     thenDragTo: self.point(stickX+41,stickY,width:390,height:400,in:controller),
                     withVelocity: .slow, thenHoldForDuration: 0.2)
        self.waitForText("Static | idle", in: status)
        XCTAssertTrue((status.value as? String ?? "").contains("analogStickRightPeak=1.000"))
        app.buttons["themeMenu"].tap()
        app.buttons["Animate"].tap()
        self.waitForText("Rive | idle", in: status)
        for (index, orientation) in [UIDeviceOrientation.landscapeLeft, .landscapeRight].enumerated()
        {
            XCUIDevice.shared.orientation = orientation
            self.waitForText("Rive | idle", in: status)
            self.waitForValue("traits=iphone-edgeToEdge-landscape", in: status)
            self.waitForValue("safeAreaContainsController=true", in: status)
            self.point(crystal ? 785 : 735,crystal ? 193 : 260,width:844,height:390,in:controller).tap()
            self.waitForText("a:\(index+2)/\(index+2)", in: status)
            // Exercise both edges when the notch switches sides.
            self.point(crystal ? 57 : 44,crystal ? 310 : 139,width:844,height:390,in:controller).tap()
            self.waitForValue("left:\(index+2)/\(index+2)", in: status)
            self.point(crystal ? 792 : 784,crystal ? 315 : 145,width:844,height:390,in:controller).tap()
            self.waitForValue("cRight:\(index+2)/\(index+2)", in: status)
            if argument == "--crystal"
            {
                self.point(774,22,width:844,height:390,in:controller).tap()
                self.waitForValue("z:\(index*2+3)/\(index*2+3)", in: status)
                self.point(70,22,width:844,height:390,in:controller).tap()
                self.waitForValue("z:\(index*2+4)/\(index*2+4)", in: status)
                self.point(423,29,width:844,height:390,in:controller).tap()
                self.waitForValue("menu:\(index+2)/\(index+2)", in: status)
                self.point(423,361,width:844,height:390,in:controller).tap()
                self.waitForValue("start:\(index+2)/\(index+2)", in: status)
            }
            let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
            attachment.name = "\(argument) safe area \(orientation.rawValue)"
            attachment.lifetime = .keepAlways
            self.add(attachment)
        }
        XCUIDevice.shared.press(.home)
        app.activate()
        self.waitForText("Rive | idle", in: status)
        self.waitForValue("safeAreaContainsController=true", in: status)
        self.waitForValue("contact=false", in: status)
        if argument == "--crystal"
        {
            app.buttons["themeMenu"].tap()
            app.buttons["Run Input Demo"].tap()
            self.waitForText("a+analogStickRight+analogStickUp+b", in: status)
            let active = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
            active.name = "Crystal simultaneous LEDs and signal paths"
            active.lifetime = .keepAlways
            self.add(active)
            self.waitForText("Rive | idle", in: status)
        }
        let attachment = XCTAttachment(screenshot: XCUIScreen.main.screenshot())
        attachment.name = "Orbit N64 analog controller and mimi"
        attachment.lifetime = .keepAlways
        self.add(attachment)
    }

    private func point(_ x: CGFloat, _ y: CGFloat, width: CGFloat, height: CGFloat, in element: XCUIElement) -> XCUICoordinate
    {
        return element.coordinate(withNormalizedOffset: CGVector(dx: x / width, dy: y / height))
    }

    private func waitForText(_ text: String, in element: XCUIElement)
    {
        let predicate = NSPredicate(format: "label CONTAINS %@", text)
        let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
        XCTAssertEqual(XCTWaiter.wait(for: [expectation], timeout: 20), .completed, element.label)
    }

    private func waitForValue(_ text: String, in element: XCUIElement)
    {
        let predicate = NSPredicate(format: "value CONTAINS %@", text)
        let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
        XCTAssertEqual(XCTWaiter.wait(for: [expectation], timeout: 20), .completed, element.value as? String ?? "")
    }
}
