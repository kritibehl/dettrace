#include "dettrace/control_loop.hpp"

#include <cassert>
#include <string>

int main() {
    auto good = dettrace::run_known_good_control_loop();
    auto bad = dettrace::run_known_bad_control_loop();

    good.report = dettrace::analyze_control_divergence(good.scenario_name, good.steps, good.steps);
    bad.report = dettrace::analyze_control_divergence(bad.scenario_name, good.steps, bad.steps);

    assert(!good.steps.empty());
    assert(good.steps.size() == bad.steps.size());

    assert(good.report.first_divergence_step == -1);
    assert(good.report.missed_deadlines == 0);
    assert(good.report.missed_deadlines == 0);

    assert(bad.report.first_divergence_step >= 0);
    assert(bad.report.first_divergence_time_s >= 0.0);
    assert(bad.report.error_growth_after_divergence >= 0.0);
    assert(bad.report.max_position_error > 0.5);
    assert(bad.report.missed_deadlines >= 1);
    assert(bad.report.output_clipping_detected);
    assert(bad.report.unstable_oscillation_detected);
    assert(bad.report.max_timing_jitter_ms > 0.0);

    bool saw_delay = false, saw_drop = false, saw_clip = false, saw_missed = false, saw_stale = false, saw_jitter = false;
    for (const auto& c : bad.report.root_cause_classes) {
        if (c == "delayed_measurement") saw_delay = true;
        if (c == "dropped_sensor_sample") saw_drop = true;
        if (c == "actuator_saturation") saw_clip = true;
        if (c == "missed_update_cycle") saw_missed = true;
        if (c == "stale_state_estimate") saw_stale = true;
        if (c == "timing_jitter") saw_jitter = true;
    }

    assert(saw_delay);
    assert(saw_drop);
    assert(saw_clip);
    assert(saw_missed);
    assert(saw_stale);
    assert(saw_jitter);

    const auto report_json = dettrace::control_report_json(bad.report);
    assert(report_json.find("first_divergence_step") != std::string::npos);
    assert(report_json.find("root_cause_classes") != std::string::npos);

    const auto timing_json = dettrace::timing_budget_summary_json(good.steps, bad.steps);
    assert(timing_json.find("actual_missed_deadlines") != std::string::npos);
    assert(timing_json.find("max_timing_jitter_ms") != std::string::npos);

    return 0;
}
