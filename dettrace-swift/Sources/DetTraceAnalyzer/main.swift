import Foundation
import DetTraceAnalyzerCore

@main
struct DetTraceAnalyzerCLI {
    static func main() async {
        do {
            let args = CommandLine.arguments
            guard args.count == 3 else {
                throw TraceError.invalidArguments
            }

            let expectedPath = args[1]
            let actualPath = args[2]

            let report = try await DivergenceAnalyzer.analyze(
                expectedPath: expectedPath,
                actualPath: actualPath
            )

            let repoRoot = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
                .deletingLastPathComponent()

            try await ReportWriter.writeReports(report, repoRoot: repoRoot)

            print("Swift divergence analysis complete.")
            if let idx = report.firstDivergenceEvent {
                print("First divergence event: \(idx)")
            } else {
                print("No divergence found.")
            }
            print("Wrote reports/divergence_report_swift.json")
            print("Wrote reports/divergence_report_swift.md")
        } catch {
            fputs("Error: \(error)\n", stderr)
            Foundation.exit(1)
        }
    }
}
