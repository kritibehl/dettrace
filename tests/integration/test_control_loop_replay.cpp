#include "dettrace/control_loop.hpp"

#include <cassert>
#include <string>
#include <vector>

static bool has_class(const dettrace::ControlLoopReport& report, const std::string& klass) {
    for (const auto& c : report.root_cause_classes) {
        if (c == klass) return true;
    }
    return false;
}

int main() {
    auto runs = dettrace::run_control_loop_scenario_pack();
    assert(runs.size() == 4);

    auto healthy = runs[0];
    healthy.report = dettrace::analyze_control_divergence(healthy.scenario_name, healthy.steps, healthy.steps);

    assert(healthy.scenario_name == "healthy");
    assert(healthy.report.first_divergence_step == -1);
    assert(healthy.report.missed_deadlines == 0);
    assert(healthy.report.max_timing_jitter_ms == 0.0);

    std::vector<dettrace::ControlLoopRun> faulted;
    for (size_t i = 1; i < runs.size(); ++i) {
        runs[i].report = dettrace::analyze_control_divergence(runs[i].scenario_name, healthy.steps, runs[i].steps);
        faulted.push_back(runs[i]);
    }

    assert(faulted[0].scenario_name == "delayed_sensor");
    assert(faulted[1].scenario_name == "actuator_saturation");
    assert(faulted[2].scenario_name == "timing_jitter");

    assert(faulted[0].report.first_divergence_step >= 0);
    assert(has_class(faulted[0].report, "delayed_measurement"));
    assert(has_class(faulted[0].report, "dropped_sensor_sample"));
    assert(has_class(faulted[0].report, "stale_state_estimate"));

    assert(faulted[1].report.first_divergence_step >= 0);
    assert(faulted[1].report.output_clipping_detected);
    assert(has_class(faulted[1].report, "actuator_saturation"));

    assert(faulted[2].report.missed_deadlines >= 1);
    assert(faulted[2].report.max_timing_jitter_ms > 0.0);
    assert(has_class(faulted[2].report, "timing_jitter"));
    assert(
        faulted[2].report.first_divergence_step >= 0 ||
        faulted[2].report.missed_deadlines >= 1
    );

    const auto comparison = dettrace::control_scenario_comparison_json(healthy, faulted);
    assert(comparison.find("delayed_sensor") != std::string::npos);
    assert(comparison.find("actuator_saturation") != std::string::npos);
    assert(comparison.find("timing_jitter") != std::string::npos);
    assert(comparison.find("divergence_step") != std::string::npos);

    const auto compact = dettrace::control_loop_diagnostics_summary_json(faulted);
    assert(compact.find("first_divergence_timestamp_s") != std::string::npos);
    assert(compact.find("deadline_misses") != std::string::npos);
    assert(compact.find("instability_detected") != std::string::npos);

    return 0;
}
