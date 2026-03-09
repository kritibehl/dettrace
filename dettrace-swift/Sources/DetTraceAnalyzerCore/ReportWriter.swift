import Foundation

public enum ReportWriter {
    public static func writeReports(_ report: DivergenceReport, repoRoot: URL) async throws {
        let reportsDir = repoRoot.appendingPathComponent("reports", isDirectory: true)
        try FileManager.default.createDirectory(at: reportsDir, withIntermediateDirectories: true)

        async let jsonWrite: Void = writeJSON(report, to: reportsDir.appendingPathComponent("divergence_report_swift.json"))
        async let mdWrite: Void = writeMarkdown(report, to: reportsDir.appendingPathComponent("divergence_report_swift.md"))

        _ = try await (jsonWrite, mdWrite)
    }

    private static func writeJSON(_ report: DivergenceReport, to url: URL) throws {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        let data = try encoder.encode(report)
        try data.write(to: url)
    }

    private static func writeMarkdown(_ report: DivergenceReport, to url: URL) throws {
        var md = "# Swift Divergence Report\n\n"
        md += "- Trace A: `\(report.traceA)`\n"
        md += "- Trace B: `\(report.traceB)`\n"
        if let idx = report.firstDivergenceEvent {
            md += "- First divergence event: `\(idx)`\n"
        } else {
            md += "- First divergence event: `none`\n"
        }
        md += "\n## Expected\n\n"
        if let expected = report.expected {
            md += """
            - seq: `\(expected.seq)`
            - type: `\(expected.type)`
            - task: `\(expected.task)`
            - worker: `\(expected.worker.map(String.init) ?? "null")`
            - queue: `\(expected.queue.map(String.init) ?? "null")`

            """
        } else {
            md += "- none\n\n"
        }

        md += "## Actual\n\n"
        if let actual = report.actual {
            md += """
            - seq: `\(actual.seq)`
            - type: `\(actual.type)`
            - task: `\(actual.task)`
            - worker: `\(actual.worker.map(String.init) ?? "null")`
            - queue: `\(actual.queue.map(String.init) ?? "null")`

            """
        } else {
            md += "- none\n\n"
        }

        md += "## Notes\n\n\(report.notes)\n"
        try md.write(to: url, atomically: true, encoding: .utf8)
    }
}
