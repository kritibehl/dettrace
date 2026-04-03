#include "dettrace/control_loop.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>

namespace fs = std::filesystem;

static void write_file(const std::string& path, const std::string& body) {
    std::ofstream out(path);
    out << body;
}

int main() {
    fs::create_directories("artifacts");
    fs::create_directories("reports");

    const auto expected = dettrace::run_expected_control_loop();
    const auto actual = dettrace::run_fault_injected_control_loop();
    const auto report = dettrace::analyze_control_divergence(expected, actual);

    dettrace::write_control_trace_jsonl("artifacts/control_expected.jsonl", expected);
    dettrace::write_control_trace_jsonl("artifacts/control_actual.jsonl", actual);
    write_file("reports/control_loop_divergence_report.json", dettrace::control_report_json(report));

    std::cout << "Control loop replay demo complete\n";
    std::cout << "Generated:\n";
    std::cout << "  artifacts/control_expected.jsonl\n";
    std::cout << "  artifacts/control_actual.jsonl\n";
    std::cout << "  reports/control_loop_divergence_report.json\n";
    return 0;
}
