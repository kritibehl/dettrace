import XCTest
import Foundation
@testable import DetTraceAnalyzerCore

final class DetTraceAnalyzerTests: XCTestCase {
    private func writeJSONL(_ events: [TraceEvent], to path: String) throws {
        let encoder = JSONEncoder()
        let lines = try events.map { event -> String in
            let data = try encoder.encode(event)
            return String(data: data, encoding: .utf8)!
        }
        try lines.joined(separator: "\n").write(toFile: path, atomically: true, encoding: .utf8)
    }

    private func tempFile(_ name: String) -> String {
        URL(fileURLWithPath: NSTemporaryDirectory())
            .appendingPathComponent(name)
            .path
    }

    func testIdenticalTracesReportNoDivergence() async throws {
        let events = [
            TraceEvent(seq: 0, type: "TASK_ENQUEUED", task: 1, worker: nil, queue: 0),
            TraceEvent(seq: 1, type: "TASK_DEQUEUED", task: 1, worker: 0, queue: 0)
        ]

        let expectedPath = tempFile("identical_expected.jsonl")
        let actualPath = tempFile("identical_actual.jsonl")

        try writeJSONL(events, to: expectedPath)
        try writeJSONL(events, to: actualPath)

        let report = try await DivergenceAnalyzer.analyze(expectedPath: expectedPath, actualPath: actualPath)

        XCTAssertNil(report.firstDivergenceEvent)
        XCTAssertNil(report.expected)
        XCTAssertNil(report.actual)
    }

    func testKnownDivergenceAtIndexFive() async throws {
        let expected = [
            TraceEvent(seq: 0, type: "TASK_ENQUEUED", task: 1, worker: nil, queue: 0),
            TraceEvent(seq: 1, type: "TASK_ENQUEUED", task: 2, worker: nil, queue: 0),
            TraceEvent(seq: 2, type: "TASK_ENQUEUED", task: 3, worker: nil, queue: 0),
            TraceEvent(seq: 3, type: "TASK_ENQUEUED", task: 4, worker: nil, queue: 0),
            TraceEvent(seq: 4, type: "TASK_ENQUEUED", task: 5, worker: nil, queue: 0),
            TraceEvent(seq: 5, type: "TASK_DEQUEUED", task: 1, worker: 0, queue: 0)
        ]

        let actual = [
            TraceEvent(seq: 0, type: "TASK_ENQUEUED", task: 1, worker: nil, queue: 0),
            TraceEvent(seq: 1, type: "TASK_ENQUEUED", task: 2, worker: nil, queue: 0),
            TraceEvent(seq: 2, type: "TASK_ENQUEUED", task: 3, worker: nil, queue: 0),
            TraceEvent(seq: 3, type: "TASK_ENQUEUED", task: 4, worker: nil, queue: 0),
            TraceEvent(seq: 4, type: "TASK_ENQUEUED", task: 5, worker: nil, queue: 0),
            TraceEvent(seq: 5, type: "TASK_DEQUEUED", task: 2, worker: 0, queue: 0)
        ]

        let expectedPath = tempFile("divergence_expected.jsonl")
        let actualPath = tempFile("divergence_actual.jsonl")

        try writeJSONL(expected, to: expectedPath)
        try writeJSONL(actual, to: actualPath)

        let report = try await DivergenceAnalyzer.analyze(expectedPath: expectedPath, actualPath: actualPath)

        XCTAssertEqual(report.firstDivergenceEvent, 5)
        XCTAssertEqual(report.expected?.task, 1)
        XCTAssertEqual(report.actual?.task, 2)
    }

    func testDifferentLengthTracesHandledSafely() async throws {
        let expected = [
            TraceEvent(seq: 0, type: "TASK_ENQUEUED", task: 1, worker: nil, queue: 0),
            TraceEvent(seq: 1, type: "TASK_DEQUEUED", task: 1, worker: 0, queue: 0),
            TraceEvent(seq: 2, type: "TASK_FINISHED", task: 1, worker: 0, queue: nil)
        ]

        let actual = [
            TraceEvent(seq: 0, type: "TASK_ENQUEUED", task: 1, worker: nil, queue: 0),
            TraceEvent(seq: 1, type: "TASK_DEQUEUED", task: 1, worker: 0, queue: 0)
        ]

        let expectedPath = tempFile("length_expected.jsonl")
        let actualPath = tempFile("length_actual.jsonl")

        try writeJSONL(expected, to: expectedPath)
        try writeJSONL(actual, to: actualPath)

        let report = try await DivergenceAnalyzer.analyze(expectedPath: expectedPath, actualPath: actualPath)

        XCTAssertEqual(report.firstDivergenceEvent, 2)
        XCTAssertEqual(report.expected?.task, 1)
        XCTAssertNil(report.actual)
    }
}
