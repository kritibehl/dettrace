#include "dettrace/control_loop.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>

namespace fs = std::filesystem;

static void write_file(const std::string& path, const std::string& body) {
    std::ofstream out(path);
    out << body;
}

int main() {
    fs::create_directories("artifacts");
    fs::create_directories("reports");

    auto runs = dettrace::run_control_loop_scenario_pack();
    auto expected = runs.front();
    expected.report = dettrace::analyze_control_divergence(expected.scenario_name, expected.steps, expected.steps);

    std::vector<dettrace::ControlLoopRun> faulted;
    for (size_t i = 1; i < runs.size(); ++i) {
        runs[i].report = dettrace::analyze_control_divergence(runs[i].scenario_name, expected.steps, runs[i].steps);
        faulted.push_back(runs[i]);
    }

    dettrace::write_control_trace_jsonl("artifacts/control_healthy.jsonl", expected.steps);
    write_file("reports/control_healthy_report.json", dettrace::control_report_json(expected.report));

    for (const auto& run : faulted) {
        dettrace::write_control_trace_jsonl("artifacts/control_" + run.scenario_name + ".jsonl", run.steps);
        dettrace::write_control_trajectory_csv("artifacts/control_" + run.scenario_name + "_trajectory.csv", expected.steps, run.steps);
        dettrace::write_control_trajectory_svg("artifacts/control_" + run.scenario_name + "_trajectory.svg", expected.steps, run.steps, run.scenario_name + " trajectory");
        write_file("reports/control_" + run.scenario_name + "_report.json", dettrace::control_report_json(run.report));
        write_file("reports/control_" + run.scenario_name + "_timing_budget.json",
                   dettrace::timing_budget_summary_json(expected.steps, run.steps));
    }

    write_file("reports/control_scenario_comparison.json",
               dettrace::control_scenario_comparison_json(expected, faulted));
    dettrace::write_control_debug_summary_svg("reports/control_debug_summary.svg", expected, faulted);

    std::cout << "Control loop replay scenario pack complete\n";
    std::cout << "Generated summary artifacts:\n";
    std::cout << "  reports/control_debug_summary.svg\n";
    std::cout << "  reports/control_scenario_comparison.json\n";
    std::cout << "Scenario reports:\n";
    for (const auto& run : faulted) {
        std::cout << "  reports/control_" << run.scenario_name << "_report.json\n";
        std::cout << "  reports/control_" << run.scenario_name << "_timing_budget.json\n";
        std::cout << "  artifacts/control_" << run.scenario_name << "_trajectory.svg\n";
    }
    return 0;
}
