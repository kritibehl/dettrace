import Foundation

let path = CommandLine.arguments.count > 1
    ? CommandLine.arguments[1]
    : "exports/replay_session_001.json"

do {
    let data = try Data(contentsOf: URL(fileURLWithPath: path))
    let object = try JSONSerialization.jsonObject(with: data) as? [String: Any]

    let divergence = object?["divergence_summary"] as? [String: Any]
    let root = object?["root_cause_panel"] as? [String: Any]

    print("DeviceReplayCLI")
    print("===============")
    print("file: \(path)")
    print("first_divergence_index: \(divergence?["first_divergence_index"] ?? "unknown")")
    print("expected_event: \(divergence?["expected_event"] ?? "unknown")")
    print("actual_event: \(divergence?["actual_event"] ?? "unknown")")
    print("probable_root_cause: \(root?["probable_root_cause"] ?? "unknown")")
} catch {
    print("error: \(error)")
    exit(1)
}
