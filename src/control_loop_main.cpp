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

    auto good = dettrace::run_known_good_control_loop();
    auto bad = dettrace::run_known_bad_control_loop();

    good.report = dettrace::analyze_control_divergence(good.scenario_name, good.steps, good.steps);
    bad.report = dettrace::analyze_control_divergence(bad.scenario_name, good.steps, bad.steps);

    dettrace::write_control_trace_jsonl("artifacts/control_known_good.jsonl", good.steps);
    dettrace::write_control_trace_jsonl("artifacts/control_known_bad.jsonl", bad.steps);

    dettrace::write_control_trajectory_csv("artifacts/control_trajectory.csv", good.steps, bad.steps);
    dettrace::write_control_trajectory_svg("artifacts/control_trajectory.svg", good.steps, bad.steps);

    write_file("reports/control_loop_known_good_report.json", dettrace::control_report_json(good.report));
    write_file("reports/control_loop_known_bad_report.json", dettrace::control_report_json(bad.report));
    write_file("reports/control_timing_budget_summary.json", dettrace::timing_budget_summary_json(good.steps, bad.steps));

    std::cout << "Control loop replay demo complete\n";
    std::cout << "Generated:\n";
    std::cout << "  artifacts/control_known_good.jsonl\n";
    std::cout << "  artifacts/control_known_bad.jsonl\n";
    std::cout << "  artifacts/control_trajectory.csv\n";
    std::cout << "  artifacts/control_trajectory.svg\n";
    std::cout << "  reports/control_loop_known_good_report.json\n";
    std::cout << "  reports/control_loop_known_bad_report.json\n";
    std::cout << "  reports/control_timing_budget_summary.json\n";
    return 0;
}
