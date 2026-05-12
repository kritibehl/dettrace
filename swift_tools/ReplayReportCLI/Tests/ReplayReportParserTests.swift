import XCTest
import Foundation

final class ReplayReportParserTests: XCTestCase {
    func testReplayReportDecisionFields() throws {
        let json = """
        {
          "result": {
            "failing_trace_detected": true,
            "fixed_trace_passed": true,
            "c_api_divergence_index": "4",
            "probable_defect_type": "missing_interrupt_clear"
          }
        }
        """.data(using: .utf8)!

        struct ReplaySummary: Codable {
            let result: ReplayResult
        }

        struct ReplayResult: Codable {
            let failing_trace_detected: Bool
            let fixed_trace_passed: Bool
            let c_api_divergence_index: String?
            let probable_defect_type: String?
        }

        let summary = try JSONDecoder().decode(ReplaySummary.self, from: json)

        XCTAssertTrue(summary.result.failing_trace_detected)
        XCTAssertTrue(summary.result.fixed_trace_passed)
        XCTAssertEqual(summary.result.probable_defect_type, "missing_interrupt_clear")
    }
}
