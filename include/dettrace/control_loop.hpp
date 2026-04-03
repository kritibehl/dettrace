#pragma once

#include <string>
#include <vector>

namespace dettrace {

struct Vec2 {
    double x = 0.0;
    double y = 0.0;
};

struct ControlLoopStep {
    int step = 0;
    double t_s = 0.0;
    double loop_dt_s = 0.0;

    Vec2 waypoint;
    Vec2 position;
    Vec2 velocity;
    Vec2 measured_position;
    Vec2 state_estimate;
    Vec2 control_output;

    bool dropped_sensor_sample = false;
    bool delayed_measurement = false;
    bool stale_state_estimate = false;
    bool actuator_saturated = false;
    bool missed_update_cycle = false;
    bool timing_jitter = false;

    double position_error = 0.0;
    double loop_budget_ms = 100.0;
    double loop_elapsed_ms = 0.0;
};

struct ControlLoopReport {
    std::string scenario_name;

    int first_divergence_step = -1;
    double first_divergence_time_s = -1.0;
    double expected_error_at_divergence = 0.0;
    double actual_error_at_divergence = 0.0;
    double error_growth_after_divergence = 0.0;
    double max_position_error = 0.0;

    int missed_deadlines = 0;
    bool output_clipping_detected = false;
    bool state_estimate_drift_detected = false;
    bool unstable_oscillation_detected = false;

    double max_loop_elapsed_ms = 0.0;
    double avg_loop_elapsed_ms = 0.0;
    double max_timing_jitter_ms = 0.0;

    std::vector<std::string> root_cause_classes;
};

struct ControlLoopRun {
    std::string scenario_name;
    std::vector<ControlLoopStep> steps;
    ControlLoopReport report;
};

std::vector<Vec2> default_waypoints();

ControlLoopRun run_known_good_control_loop();
ControlLoopRun run_known_bad_control_loop();

void write_control_trace_jsonl(const std::string& path, const std::vector<ControlLoopStep>& steps);
void write_control_trajectory_csv(const std::string& path, const std::vector<ControlLoopStep>& expected,
                                  const std::vector<ControlLoopStep>& actual);
void write_control_trajectory_svg(const std::string& path, const std::vector<ControlLoopStep>& expected,
                                  const std::vector<ControlLoopStep>& actual);
std::string timing_budget_summary_json(const std::vector<ControlLoopStep>& expected,
                                       const std::vector<ControlLoopStep>& actual);
ControlLoopReport analyze_control_divergence(const std::string& scenario_name,
                                             const std::vector<ControlLoopStep>& expected,
                                             const std::vector<ControlLoopStep>& actual);
std::string control_report_json(const ControlLoopReport& report);

}  // namespace dettrace
