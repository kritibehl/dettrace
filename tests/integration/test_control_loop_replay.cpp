#include "dettrace/control_loop.hpp"

#include <cassert>
#include <fstream>
#include <sstream>
#include <string>

static std::string slurp(const std::string& path) {
    std::ifstream in(path);
    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

int main() {
    const auto expected = dettrace::run_expected_control_loop();
    const auto actual = dettrace::run_fault_injected_control_loop();
    const auto report = dettrace::analyze_control_divergence(expected, actual);

    assert(expected.size() == actual.size());
    assert(!expected.empty());

    assert(report.first_divergence_step >= 0);
    assert(report.first_divergence_time_s >= 0.0);
    assert(report.error_growth_after_divergence > 0.0);
    assert(report.max_position_error > 0.5);
    assert(report.missed_deadlines >= 1);
    assert(report.output_clipping_detected);
    bool saw_state_drift_class = false;
    for (const auto& c : report.root_cause_classes) {
        if (c == "state_estimate_drift") saw_state_drift_class = true;
    }
    assert(report.state_estimate_drift_detected == saw_state_drift_class);

    bool saw_delay = false, saw_drop = false, saw_clip = false, saw_missed = false;
    for (const auto& c : report.root_cause_classes) {
        if (c == "delayed_measurement") saw_delay = true;
        if (c == "dropped_sensor_sample") saw_drop = true;
        if (c == "actuator_saturation") saw_clip = true;
        if (c == "missed_update_cycle") saw_missed = true;
    }

    assert(saw_delay);
    assert(saw_drop);
    assert(saw_clip);
    assert(saw_missed);

    const auto json = dettrace::control_report_json(report);
    assert(json.find("first_divergence_step") != std::string::npos);
    assert(json.find("root_cause_classes") != std::string::npos);

    return 0;
}
