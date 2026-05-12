import XCTest
import Foundation

final class ReplayValidationTests: XCTestCase {
    func testMissingInterruptClearReplayResult() throws {
        let replayResult = ReplayResult(
            firstDivergenceIndex: 4,
            expectedEvent: "interrupt_cleared",
            actualEvent: "sensor_read",
            probableDefectType: "missing_interrupt_clear",
            rootCause: "Interrupt was not cleared before the next device read"
        )

        XCTAssertEqual(replayResult.firstDivergenceIndex, 4)
        XCTAssertEqual(replayResult.expectedEvent, "interrupt_cleared")
        XCTAssertEqual(replayResult.actualEvent, "sensor_read")
        XCTAssertEqual(replayResult.probableDefectType, "missing_interrupt_clear")
        XCTAssertTrue(replayResult.rootCause.contains("Interrupt"))
    }

    func testReplayDecision() throws {
        let decision = ReplayDecision(
            expectedStatus: "PASS",
            actualStatus: "FAIL",
            rootCause: "missing_interrupt_clear"
        )

        XCTAssertEqual(decision.expectedStatus, "PASS")
        XCTAssertEqual(decision.actualStatus, "FAIL")
        XCTAssertEqual(decision.rootCause, "missing_interrupt_clear")
        XCTAssertTrue(decision.isRegression)
    }
}

struct ReplayResult {
    let firstDivergenceIndex: Int
    let expectedEvent: String
    let actualEvent: String
    let probableDefectType: String
    let rootCause: String
}

struct ReplayDecision {
    let expectedStatus: String
    let actualStatus: String
    let rootCause: String

    var isRegression: Bool {
        expectedStatus == "PASS" && actualStatus == "FAIL"
    }
}
