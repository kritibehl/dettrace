// swift-tools-version: 5.7
import PackageDescription

let package = Package(
    name: "DetTraceAnalyzer",
    products: [
        .library(
            name: "DetTraceAnalyzerCore",
            targets: ["DetTraceAnalyzerCore"]
        ),
        .executable(
            name: "DetTraceAnalyzer",
            targets: ["DetTraceAnalyzer"]
        )
    ],
    targets: [
        .target(
            name: "DetTraceAnalyzerCore",
            path: "Sources/DetTraceAnalyzerCore"
        ),
        .executableTarget(
            name: "DetTraceAnalyzer",
            dependencies: ["DetTraceAnalyzerCore"],
            path: "Sources/DetTraceAnalyzer"
        ),
        .testTarget(
            name: "DetTraceAnalyzerTests",
            dependencies: ["DetTraceAnalyzerCore"],
            path: "Tests/DetTraceAnalyzerTests"
        )
    ]
)
