#include "dettrace/control_loop.hpp"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <set>
#include <sstream>
#include <stdexcept>

namespace dettrace {
namespace {

constexpr double kDt = 0.1;
constexpr int kSteps = 80;
constexpr double kKp = 1.4;
constexpr double kKd = 0.45;
constexpr double kMaxAccel = 1.2;
constexpr double kDivergenceThreshold = 0.75;

double norm(const Vec2& v) {
    return std::sqrt(v.x * v.x + v.y * v.y);
}

Vec2 add(const Vec2& a, const Vec2& b) {
    return {a.x + b.x, a.y + b.y};
}

Vec2 sub(const Vec2& a, const Vec2& b) {
    return {a.x - b.x, a.y - b.y};
}

Vec2 scale(const Vec2& v, double s) {
    return {v.x * s, v.y * s};
}

Vec2 clamp_vec(const Vec2& v, double max_mag, bool& clipped) {
    const double mag = norm(v);
    if (mag <= max_mag || mag == 0.0) return v;
    clipped = true;
    return scale(v, max_mag / mag);
}

Vec2 waypoint_for_step(int step, const std::vector<Vec2>& waypoints) {
    const int segment = std::min<int>(step / 20, static_cast<int>(waypoints.size()) - 1);
    return waypoints[segment];
}

std::vector<ControlLoopStep> run_loop(bool inject_faults) {
    std::vector<ControlLoopStep> out;
    out.reserve(kSteps);

    const auto waypoints = default_waypoints();
    Vec2 pos{0.0, 0.0};
    Vec2 vel{0.0, 0.0};
    Vec2 prev_measured = pos;
    Vec2 delayed_buffer = pos;

    for (int step = 0; step < kSteps; ++step) {
        const double t = step * kDt;
        const Vec2 wp = waypoint_for_step(step, waypoints);

        ControlLoopStep s;
        s.step = step;
        s.t_s = t;
        s.waypoint = wp;
        s.position = pos;
        s.velocity = vel;

        Vec2 measured = pos;
        if (inject_faults) {
            if (step == 18 || step == 37) {
                s.dropped_sensor_sample = true;
                measured = prev_measured;
            }
            if (step >= 24 && step <= 31) {
                s.delayed_measurement = true;
                measured = delayed_buffer;
            }
            delayed_buffer = pos;
        }

        s.measured_position = measured;
        prev_measured = measured;

        const Vec2 error = sub(wp, measured);
        Vec2 accel_cmd = add(scale(error, kKp), scale(vel, -kKd));

        bool clipped = false;
        if (inject_faults && (step >= 28 && step <= 45)) {
            accel_cmd = clamp_vec(accel_cmd, 0.55, clipped);
        } else {
            accel_cmd = clamp_vec(accel_cmd, kMaxAccel, clipped);
        }
        s.actuator_saturated = clipped;

        if (inject_faults && (step == 33 || step == 34)) {
            s.missed_update_cycle = true;
            accel_cmd = {0.0, 0.0};
        }

        s.control_output = accel_cmd;

        vel = add(vel, scale(accel_cmd, kDt));
        pos = add(pos, scale(vel, kDt));

        s.position = pos;
        s.velocity = vel;
        s.position_error = norm(sub(wp, pos));

        out.push_back(s);
    }

    return out;
}

std::string json_bool(bool v) { return v ? "true" : "false"; }

}  // namespace

std::vector<Vec2> default_waypoints() {
    return {
        {1.0, 0.8},
        {2.2, 1.8},
        {3.5, 1.1},
        {4.2, 2.6}
    };
}

std::vector<ControlLoopStep> run_expected_control_loop() {
    return run_loop(false);
}

std::vector<ControlLoopStep> run_fault_injected_control_loop() {
    return run_loop(true);
}

void write_control_trace_jsonl(const std::string& path, const std::vector<ControlLoopStep>& steps) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("failed to open " + path);

    for (const auto& s : steps) {
        out << "{"
            << "\"step\":" << s.step << ","
            << "\"t_s\":" << s.t_s << ","
            << "\"waypoint\":{\"x\":" << s.waypoint.x << ",\"y\":" << s.waypoint.y << "},"
            << "\"position\":{\"x\":" << s.position.x << ",\"y\":" << s.position.y << "},"
            << "\"velocity\":{\"x\":" << s.velocity.x << ",\"y\":" << s.velocity.y << "},"
            << "\"measured_position\":{\"x\":" << s.measured_position.x << ",\"y\":" << s.measured_position.y << "},"
            << "\"control_output\":{\"x\":" << s.control_output.x << ",\"y\":" << s.control_output.y << "},"
            << "\"dropped_sensor_sample\":" << json_bool(s.dropped_sensor_sample) << ","
            << "\"delayed_measurement\":" << json_bool(s.delayed_measurement) << ","
            << "\"actuator_saturated\":" << json_bool(s.actuator_saturated) << ","
            << "\"missed_update_cycle\":" << json_bool(s.missed_update_cycle) << ","
            << "\"position_error\":" << s.position_error
            << "}\n";
    }
}

ControlLoopReport analyze_control_divergence(const std::vector<ControlLoopStep>& expected,
                                             const std::vector<ControlLoopStep>& actual) {
    ControlLoopReport r;
    std::set<std::string> causes;

    const int n = std::min<int>(expected.size(), actual.size());
    for (int i = 0; i < n; ++i) {
        const auto& e = expected[i];
        const auto& a = actual[i];

        const double pos_gap = norm(sub(e.position, a.position));
        r.max_position_error = std::max(r.max_position_error, a.position_error);

        if (a.missed_update_cycle) r.missed_deadlines++;
        if (a.actuator_saturated) r.output_clipping_detected = true;

        const double meas_gap = norm(sub(a.position, a.measured_position));
        if (meas_gap > 0.35) r.state_estimate_drift_detected = true;

        if (i >= 4) {
            const double e1 = actual[i].position_error;
            const double e2 = actual[i - 1].position_error;
            const double e3 = actual[i - 2].position_error;
            if (e1 > e2 && e2 > e3 && e1 > 1.1) {
                r.unstable_oscillation_detected = true;
            }
        }

        if (r.first_divergence_step == -1 && pos_gap > kDivergenceThreshold) {
            r.first_divergence_step = i;
            r.first_divergence_time_s = a.t_s;
            r.expected_error_at_divergence = e.position_error;
            r.actual_error_at_divergence = a.position_error;
        }

        if (a.dropped_sensor_sample) causes.insert("dropped_sensor_sample");
        if (a.delayed_measurement) causes.insert("delayed_measurement");
        if (a.actuator_saturated) causes.insert("actuator_saturation");
        if (a.missed_update_cycle) causes.insert("missed_update_cycle");
    }

    if (r.first_divergence_step >= 0) {
        double peak_error_after_divergence = r.actual_error_at_divergence;
        for (int i = r.first_divergence_step; i < n; ++i) {
            peak_error_after_divergence = std::max(peak_error_after_divergence, actual[i].position_error);
        }
        r.error_growth_after_divergence = peak_error_after_divergence - r.actual_error_at_divergence;
    }

    if (r.state_estimate_drift_detected) causes.insert("state_estimate_drift");
    if (r.output_clipping_detected) causes.insert("controller_output_clipping");
    if (r.unstable_oscillation_detected) causes.insert("unstable_oscillation");

    r.root_cause_classes.assign(causes.begin(), causes.end());
    return r;
}

std::string control_report_json(const ControlLoopReport& report) {
    std::ostringstream oss;
    oss << "{\n"
        << "  \"first_divergence_step\": " << report.first_divergence_step << ",\n"
        << "  \"first_divergence_time_s\": " << report.first_divergence_time_s << ",\n"
        << "  \"expected_error_at_divergence\": " << report.expected_error_at_divergence << ",\n"
        << "  \"actual_error_at_divergence\": " << report.actual_error_at_divergence << ",\n"
        << "  \"error_growth_after_divergence\": " << report.error_growth_after_divergence << ",\n"
        << "  \"max_position_error\": " << report.max_position_error << ",\n"
        << "  \"missed_deadlines\": " << report.missed_deadlines << ",\n"
        << "  \"output_clipping_detected\": " << (report.output_clipping_detected ? "true" : "false") << ",\n"
        << "  \"state_estimate_drift_detected\": " << (report.state_estimate_drift_detected ? "true" : "false") << ",\n"
        << "  \"unstable_oscillation_detected\": " << (report.unstable_oscillation_detected ? "true" : "false") << ",\n"
        << "  \"root_cause_classes\": [";
    for (size_t i = 0; i < report.root_cause_classes.size(); ++i) {
        if (i) oss << ",";
        oss << "\"" << report.root_cause_classes[i] << "\"";
    }
    oss << "]\n}\n";
    return oss.str();
}

}  // namespace dettrace
