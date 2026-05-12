import Foundation

struct ReplaySummary: Codable {
    let result: ReplayResult
}

struct ReplayResult: Codable {
    let failing_trace_detected: Bool
    let fixed_trace_passed: Bool
    let c_api_divergence_index: String?
    let probable_defect_type: String?
}

let path = CommandLine.arguments.count > 1
    ? CommandLine.arguments[1]
    : "device_replay/reports/device_replay_summary.json"

let url = URL(fileURLWithPath: path)

do {
    let data = try Data(contentsOf: url)
    let summary = try JSONDecoder().decode(ReplaySummary.self, from: data)

    print("Replay Report Summary")
    print("====================")
    print("failing_trace_detected: \(summary.result.failing_trace_detected)")
    print("fixed_trace_passed: \(summary.result.fixed_trace_passed)")
    print("probable_defect_type: \(summary.result.probable_defect_type ?? "unknown")")

    if summary.result.failing_trace_detected && summary.result.fixed_trace_passed {
        print("decision: replay_regression_reproduced_and_fixed")
    } else {
        print("decision: needs_investigation")
    }
} catch {
    print("error: \(error)")
    exit(1)
}
