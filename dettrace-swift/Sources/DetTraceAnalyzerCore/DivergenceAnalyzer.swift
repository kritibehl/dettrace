import Foundation

public enum DivergenceAnalyzer {
    public static func analyze(expectedPath: String, actualPath: String) async throws -> DivergenceReport {
        let store = AnalysisStore()

        async let expectedEvents = TraceReader.readJSONL(from: expectedPath)
        async let actualEvents = TraceReader.readJSONL(from: actualPath)

        let (expected, actual) = try await (expectedEvents, actualEvents)

        await store.setExpected(expected)
        await store.setActual(actual)
        await store.computeFirstDivergence()

        return await store.buildReport(expectedPath: expectedPath, actualPath: actualPath)
    }
}
