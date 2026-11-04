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
}
