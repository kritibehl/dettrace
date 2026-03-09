import Foundation

public enum TraceReader {
    public static func readJSONL(from path: String) async throws -> [TraceEvent] {
        let url = URL(fileURLWithPath: path)

        guard FileManager.default.fileExists(atPath: url.path) else {
            throw TraceError.invalidFile(path)
        }

        let data = try Data(contentsOf: url)
        guard let text = String(data: data, encoding: .utf8) else {
            throw TraceError.invalidFile(path)
        }

        let decoder = JSONDecoder()

        return try text
            .split(whereSeparator: \.isNewline)
            .map { line in
                let lineString = String(line)
                guard let lineData = lineString.data(using: .utf8) else {
                    throw TraceError.invalidJSONLine(lineString)
                }
                do {
                    return try decoder.decode(TraceEvent.self, from: lineData)
                } catch {
                    throw TraceError.invalidJSONLine(lineString)
                }
            }
    }
}
