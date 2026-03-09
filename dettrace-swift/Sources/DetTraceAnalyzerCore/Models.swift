import Foundation

public enum TraceError: Error, CustomStringConvertible {
    case invalidArguments
    case invalidFile(String)
    case invalidJSONLine(String)

    public var description: String {
        switch self {
        case .invalidArguments:
            return "Usage: swift run DetTraceAnalyzer <expected.jsonl> <actual.jsonl>"
        case .invalidFile(let path):
            return "Could not read file at path: \(path)"
        case .invalidJSONLine(let line):
            return "Invalid JSONL line: \(line)"
        }
    }
}

public struct TraceEvent: Codable, Equatable, Sendable {
    public let seq: Int
    public let type: String
    public let task: Int
    public let worker: Int?
    public let queue: Int?

    public init(seq: Int, type: String, task: Int, worker: Int?, queue: Int?) {
        self.seq = seq
        self.type = type
        self.task = task
        self.worker = worker
        self.queue = queue
    }
}

public struct DivergenceReport: Codable, Sendable {
    public let traceA: String
    public let traceB: String
    public let firstDivergenceEvent: Int?
    public let expected: TraceEvent?
    public let actual: TraceEvent?
    public let notes: String

    public init(
        traceA: String,
        traceB: String,
        firstDivergenceEvent: Int?,
        expected: TraceEvent?,
        actual: TraceEvent?,
        notes: String
    ) {
        self.traceA = traceA
        self.traceB = traceB
        self.firstDivergenceEvent = firstDivergenceEvent
        self.expected = expected
        self.actual = actual
        self.notes = notes
    }

    enum CodingKeys: String, CodingKey {
        case traceA = "trace_a"
        case traceB = "trace_b"
        case firstDivergenceEvent = "first_divergence_event"
        case expected
        case actual
        case notes
    }
}
