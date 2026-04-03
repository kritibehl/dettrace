#include "dettrace/control_loop.hpp"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>

namespace dettrace {
namespace {

constexpr double kNominalDt = 0.1;
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

std::string json_bool(bool v) { return v ? "true" : "false"; }

double svg_x(double x) { return 60.0 + x * 90.0; }
double svg_y(double y) { return 320.0 - y * 90.0; }

std::string color_for_index(size_t idx) {
    static const char* colors[] = {"#16a34a", "#dc2626", "#ea580c", "#7c3aed", "#0891b2"};
    return colors[idx % 5];
}

std::string polyline_points(const std::vector<ControlLoopStep>& steps, bool use_waypoint) {
    std::ostringstream oss;
    for (size_t i = 0; i < steps.size(); ++i) {
        const auto& p = use_waypoint ? steps[i].waypoint : steps[i].position;
        if (i) oss << " ";
        oss << svg_x(p.x) << "," << svg_y(p.y);
    }
    return oss.str();
}

struct ScenarioFlags {
    bool delayed_sensor = false;
    bool actuator_saturation = false;
    bool timing_jitter = false;
};

ScenarioFlags flags_for(const std::string& name) {
    ScenarioFlags f;
    if (name == "delayed_sensor") f.delayed_sensor = true;
    if (name == "actuator_saturation") f.actuator_saturation = true;
    if (name == "timing_jitter") f.timing_jitter = true;
    return f;
}

ControlLoopRun run_loop(const std::string& scenario_name, const ScenarioFlags& flags) {
    ControlLoopRun run;
    run.scenario_name = scenario_name;
    run.steps.reserve(kSteps);

    const auto waypoints = default_waypoints();
    Vec2 pos{0.0, 0.0};
    Vec2 vel{0.0, 0.0};
    Vec2 prev_measured = pos;
    Vec2 delayed_buffer = pos;
    Vec2 estimate = pos;
    double t = 0.0;

    for (int step = 0; step < kSteps; ++step) {
        double dt = kNominalDt;
        double elapsed_ms = 55.0 + (step % 3) * 5.0;

        ControlLoopStep s;
        s.step = step;
        s.waypoint = waypoint_for_step(step, waypoints);
        s.loop_budget_ms = 100.0;

        if (flags.timing_jitter) {
            if (step == 16 || step == 29 || step == 41) {
                dt = 0.13;
                elapsed_ms = 123.0;
                s.timing_jitter = true;
            } else if (step == 33 || step == 34) {
                dt = 0.12;
                elapsed_ms = 118.0;
                s.timing_jitter = true;
            }
        }

        t += dt;
        s.t_s = t;
        s.loop_dt_s = dt;
        s.loop_elapsed_ms = elapsed_ms;

        s.position = pos;
        s.velocity = vel;

        Vec2 measured = pos;
        if (flags.delayed_sensor) {
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

        if (flags.delayed_sensor && step >= 26 && step <= 39) {
            s.stale_state_estimate = true;
            estimate = add(scale(estimate, 0.98), scale(prev_measured, 0.02));
        } else {
            estimate = measured;
        }
        s.state_estimate = estimate;

        const Vec2 error = sub(s.waypoint, estimate);
        Vec2 accel_cmd = add(scale(error, kKp), scale(vel, -kKd));

        bool clipped = false;
        if (flags.actuator_saturation && (step >= 28 && step <= 45)) {
            accel_cmd = clamp_vec(accel_cmd, 0.55, clipped);
        } else {
            accel_cmd = clamp_vec(accel_cmd, kMaxAccel, clipped);
        }
        s.actuator_saturated = clipped;

        if (flags.timing_jitter && (step == 33 || step == 34)) {
            s.missed_update_cycle = true;
            accel_cmd = {0.0, 0.0};
        }

        s.control_output = accel_cmd;

        vel = add(vel, scale(accel_cmd, dt));
        pos = add(pos, scale(vel, dt));

        s.position = pos;
        s.velocity = vel;
        s.position_error = norm(sub(s.waypoint, pos));

        run.steps.push_back(s);
    }

    return run;
}

}  // namespace

std::vector<Vec2> default_waypoints() {
    return {
        {1.0, 0.8},
        {2.2, 1.8},
        {3.5, 1.1},
        {4.2, 2.6}
    };
}

ControlLoopRun run_control_loop_scenario(const std::string& scenario_name) {
    if (scenario_name == "healthy") return run_loop("healthy", {});
    return run_loop(scenario_name, flags_for(scenario_name));
}

std::vector<ControlLoopRun> run_control_loop_scenario_pack() {
    return {
        run_control_loop_scenario("healthy"),
        run_control_loop_scenario("delayed_sensor"),
        run_control_loop_scenario("actuator_saturation"),
        run_control_loop_scenario("timing_jitter")
    };
}

void write_control_trace_jsonl(const std::string& path, const std::vector<ControlLoopStep>& steps) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("failed to open " + path);

    for (const auto& s : steps) {
        out << "{"
            << "\"step\":" << s.step << ","
            << "\"t_s\":" << s.t_s << ","
            << "\"loop_dt_s\":" << s.loop_dt_s << ","
            << "\"waypoint\":{\"x\":" << s.waypoint.x << ",\"y\":" << s.waypoint.y << "},"
            << "\"position\":{\"x\":" << s.position.x << ",\"y\":" << s.position.y << "},"
            << "\"velocity\":{\"x\":" << s.velocity.x << ",\"y\":" << s.velocity.y << "},"
            << "\"measured_position\":{\"x\":" << s.measured_position.x << ",\"y\":" << s.measured_position.y << "},"
            << "\"state_estimate\":{\"x\":" << s.state_estimate.x << ",\"y\":" << s.state_estimate.y << "},"
            << "\"control_output\":{\"x\":" << s.control_output.x << ",\"y\":" << s.control_output.y << "},"
            << "\"dropped_sensor_sample\":" << json_bool(s.dropped_sensor_sample) << ","
            << "\"delayed_measurement\":" << json_bool(s.delayed_measurement) << ","
            << "\"stale_state_estimate\":" << json_bool(s.stale_state_estimate) << ","
            << "\"actuator_saturated\":" << json_bool(s.actuator_saturated) << ","
            << "\"missed_update_cycle\":" << json_bool(s.missed_update_cycle) << ","
            << "\"timing_jitter\":" << json_bool(s.timing_jitter) << ","
            << "\"position_error\":" << s.position_error << ","
            << "\"loop_budget_ms\":" << s.loop_budget_ms << ","
            << "\"loop_elapsed_ms\":" << s.loop_elapsed_ms
            << "}\n";
    }
}

void write_control_trajectory_csv(const std::string& path,
                                  const std::vector<ControlLoopStep>& expected,
                                  const std::vector<ControlLoopStep>& actual) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("failed to open " + path);

    out << "step,t_s,waypoint_x,waypoint_y,expected_x,expected_y,actual_x,actual_y,expected_error,actual_error\n";
    const int n = std::min<int>(expected.size(), actual.size());
    for (int i = 0; i < n; ++i) {
        out << expected[i].step << ","
            << expected[i].t_s << ","
            << expected[i].waypoint.x << ","
            << expected[i].waypoint.y << ","
            << expected[i].position.x << ","
            << expected[i].position.y << ","
            << actual[i].position.x << ","
            << actual[i].position.y << ","
            << expected[i].position_error << ","
            << actual[i].position_error << "\n";
    }
}

void write_control_trajectory_svg(const std::string& path,
                                  const std::vector<ControlLoopStep>& expected,
                                  const std::vector<ControlLoopStep>& actual,
                                  const std::string& title) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("failed to open " + path);

    out << "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"520\" height=\"360\" viewBox=\"0 0 520 360\">\n";
    out << "<rect width=\"100%\" height=\"100%\" fill=\"white\"/>\n";
    out << "<line x1=\"40\" y1=\"320\" x2=\"480\" y2=\"320\" stroke=\"black\" stroke-width=\"1\"/>\n";
    out << "<line x1=\"60\" y1=\"20\" x2=\"60\" y2=\"320\" stroke=\"black\" stroke-width=\"1\"/>\n";
    out << "<text x=\"70\" y=\"30\" font-size=\"14\">" << title << "</text>\n";
    out << "<polyline fill=\"none\" stroke=\"#2563eb\" stroke-width=\"2\" points=\"" << polyline_points(expected, true) << "\"/>\n";
    out << "<polyline fill=\"none\" stroke=\"#16a34a\" stroke-width=\"2\" points=\"" << polyline_points(actual, false) << "\"/>\n";
    out << "<polyline fill=\"none\" stroke=\"#dc2626\" stroke-width=\"2\" points=\"" << polyline_points(actual, true) << "\"/>\n";
    out << "<text x=\"300\" y=\"40\" font-size=\"12\" fill=\"#2563eb\">Waypoint Path</text>\n";
    out << "<text x=\"300\" y=\"58\" font-size=\"12\" fill=\"#16a34a\">Expected Trajectory</text>\n";
    out << "<text x=\"300\" y=\"76\" font-size=\"12\" fill=\"#dc2626\">Actual Trajectory</text>\n";
    out << "</svg>\n";
}

ControlLoopReport analyze_control_divergence(const std::string& scenario_name,
                                             const std::vector<ControlLoopStep>& expected,
                                             const std::vector<ControlLoopStep>& actual) {
    ControlLoopReport r;
    r.scenario_name = scenario_name;
    std::set<std::string> causes;

    const int n = std::min<int>(expected.size(), actual.size());
    double sum_elapsed = 0.0;

    for (int i = 0; i < n; ++i) {
        const auto& e = expected[i];
        const auto& a = actual[i];

        const double pos_gap = norm(sub(e.position, a.position));
        r.max_position_error = std::max(r.max_position_error, a.position_error);
        r.max_loop_elapsed_ms = std::max(r.max_loop_elapsed_ms, a.loop_elapsed_ms);
        sum_elapsed += a.loop_elapsed_ms;
        r.max_timing_jitter_ms = std::max(r.max_timing_jitter_ms, std::abs(a.loop_dt_s - kNominalDt) * 1000.0);

        if (a.loop_elapsed_ms > a.loop_budget_ms) r.missed_deadlines++;
        if (a.actuator_saturated) r.output_clipping_detected = true;

        const double estimate_gap = norm(sub(a.position, a.state_estimate));
        if (estimate_gap > 0.25) r.state_estimate_drift_detected = true;

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
        if (a.stale_state_estimate) causes.insert("stale_state_estimate");
        if (a.actuator_saturated) causes.insert("actuator_saturation");
        if (a.missed_update_cycle) causes.insert("missed_update_cycle");
        if (a.timing_jitter) causes.insert("timing_jitter");
    }

    r.avg_loop_elapsed_ms = n > 0 ? sum_elapsed / n : 0.0;

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
        << "  \"scenario_name\": \"" << report.scenario_name << "\",\n"
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
        << "  \"max_loop_elapsed_ms\": " << report.max_loop_elapsed_ms << ",\n"
        << "  \"avg_loop_elapsed_ms\": " << report.avg_loop_elapsed_ms << ",\n"
        << "  \"max_timing_jitter_ms\": " << report.max_timing_jitter_ms << ",\n"
        << "  \"root_cause_classes\": [";
    for (size_t i = 0; i < report.root_cause_classes.size(); ++i) {
        if (i) oss << ",";
        oss << "\"" << report.root_cause_classes[i] << "\"";
    }
    oss << "]\n}\n";
    return oss.str();
}

std::string timing_budget_summary_json(const std::vector<ControlLoopStep>& expected,
                                       const std::vector<ControlLoopStep>& actual) {
    const int n = std::min<int>(expected.size(), actual.size());
    int expected_deadlines = 0;
    int actual_deadlines = 0;
    double max_actual_elapsed = 0.0;
    double avg_actual_elapsed = 0.0;
    double max_jitter_ms = 0.0;

    for (int i = 0; i < n; ++i) {
        if (expected[i].loop_elapsed_ms > expected[i].loop_budget_ms) expected_deadlines++;
        if (actual[i].loop_elapsed_ms > actual[i].loop_budget_ms) actual_deadlines++;
        max_actual_elapsed = std::max(max_actual_elapsed, actual[i].loop_elapsed_ms);
        avg_actual_elapsed += actual[i].loop_elapsed_ms;
        max_jitter_ms = std::max(max_jitter_ms, std::abs(actual[i].loop_dt_s - kNominalDt) * 1000.0);
    }
    if (n > 0) avg_actual_elapsed /= n;

    std::ostringstream oss;
    oss << "{\n"
        << "  \"expected_missed_deadlines\": " << expected_deadlines << ",\n"
        << "  \"actual_missed_deadlines\": " << actual_deadlines << ",\n"
        << "  \"max_actual_loop_elapsed_ms\": " << max_actual_elapsed << ",\n"
        << "  \"avg_actual_loop_elapsed_ms\": " << avg_actual_elapsed << ",\n"
        << "  \"max_timing_jitter_ms\": " << max_jitter_ms << "\n"
        << "}\n";
    return oss.str();
}

std::string control_scenario_comparison_json(const ControlLoopRun& expected,
                                             const std::vector<ControlLoopRun>& scenarios) {
    std::ostringstream oss;
    oss << "{\n"
        << "  \"reference_scenario\": \"" << expected.scenario_name << "\",\n"
        << "  \"scenarios\": [\n";

    for (size_t i = 0; i < scenarios.size(); ++i) {
        const auto& s = scenarios[i];
        const auto& r = s.report;
        oss << "    {\n"
            << "      \"scenario_name\": \"" << r.scenario_name << "\",\n"
            << "      \"divergence_step\": " << r.first_divergence_step << ",\n"
            << "      \"divergence_time_s\": " << r.first_divergence_time_s << ",\n"
            << "      \"error_growth_after_divergence\": " << r.error_growth_after_divergence << ",\n"
            << "      \"missed_deadlines\": " << r.missed_deadlines << ",\n"
            << "      \"oscillation_detected\": " << (r.unstable_oscillation_detected ? "true" : "false") << ",\n"
            << "      \"root_cause_classes\": [";
        for (size_t j = 0; j < r.root_cause_classes.size(); ++j) {
            if (j) oss << ",";
            oss << "\"" << r.root_cause_classes[j] << "\"";
        }
        oss << "]\n"
            << "    }";
        if (i + 1 < scenarios.size()) oss << ",";
        oss << "\n";
    }

    oss << "  ]\n}\n";
    return oss.str();
}

void write_control_debug_summary_svg(const std::string& path,
                                     const ControlLoopRun& expected,
                                     const std::vector<ControlLoopRun>& scenarios) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("failed to open " + path);

    out << "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"980\" height=\"620\" viewBox=\"0 0 980 620\">\n";
    out << "<rect width=\"100%\" height=\"100%\" fill=\"white\"/>\n";
    out << "<text x=\"30\" y=\"36\" font-size=\"22\" font-family=\"Arial\">Control Loop Replay & Divergence Summary</text>\n";

    out << "<line x1=\"40\" y1=\"360\" x2=\"470\" y2=\"360\" stroke=\"black\" stroke-width=\"1\"/>\n";
    out << "<line x1=\"60\" y1=\"80\" x2=\"60\" y2=\"360\" stroke=\"black\" stroke-width=\"1\"/>\n";
    out << "<text x=\"70\" y=\"95\" font-size=\"14\">Expected vs Actual Trajectories</text>\n";

    out << "<polyline fill=\"none\" stroke=\"#2563eb\" stroke-width=\"2\" points=\"" << polyline_points(expected.steps, true) << "\"/>\n";
    out << "<polyline fill=\"none\" stroke=\"#16a34a\" stroke-width=\"2\" points=\"" << polyline_points(expected.steps, false) << "\"/>\n";

    for (size_t i = 0; i < scenarios.size(); ++i) {
        const auto& s = scenarios[i];
        out << "<polyline fill=\"none\" stroke=\"" << color_for_index(i + 1) << "\" stroke-width=\"2\" points=\"" << polyline_points(s.steps, false) << "\"/>\n";
    }

    out << "<text x=\"285\" y=\"108\" font-size=\"12\" fill=\"#2563eb\">Waypoint Path</text>\n";
    out << "<text x=\"285\" y=\"126\" font-size=\"12\" fill=\"#16a34a\">Healthy Trajectory</text>\n";

    double y = 160.0;
    for (size_t i = 0; i < scenarios.size(); ++i) {
        out << "<text x=\"285\" y=\"" << y << "\" font-size=\"12\" fill=\"" << color_for_index(i + 1) << "\">"
            << scenarios[i].scenario_name << "</text>\n";
        y += 18.0;
    }

    out << "<text x=\"530\" y=\"95\" font-size=\"16\">Scenario Comparison</text>\n";
    out << "<text x=\"530\" y=\"122\" font-size=\"12\">scenario</text>\n";
    out << "<text x=\"655\" y=\"122\" font-size=\"12\">div step</text>\n";
    out << "<text x=\"730\" y=\"122\" font-size=\"12\">time(s)</text>\n";
    out << "<text x=\"800\" y=\"122\" font-size=\"12\">missed dl</text>\n";
    out << "<text x=\"885\" y=\"122\" font-size=\"12\">root cause</text>\n";

    double row_y = 150.0;
    for (size_t i = 0; i < scenarios.size(); ++i) {
        const auto& r = scenarios[i].report;
        std::ostringstream roots;
        for (size_t j = 0; j < r.root_cause_classes.size(); ++j) {
            if (j) roots << ",";
            roots << r.root_cause_classes[j];
        }
        out << "<text x=\"530\" y=\"" << row_y << "\" font-size=\"11\" fill=\"" << color_for_index(i + 1) << "\">" << r.scenario_name << "</text>\n";
        out << "<text x=\"660\" y=\"" << row_y << "\" font-size=\"11\">" << r.first_divergence_step << "</text>\n";
        out << "<text x=\"732\" y=\"" << row_y << "\" font-size=\"11\">" << r.first_divergence_time_s << "</text>\n";
        out << "<text x=\"815\" y=\"" << row_y << "\" font-size=\"11\">" << r.missed_deadlines << "</text>\n";
        out << "<text x=\"885\" y=\"" << row_y << "\" font-size=\"11\">" << roots.str() << "</text>\n";
        row_y += 26.0;
    }

    out << "<text x=\"530\" y=\"320\" font-size=\"16\">Visual Proof Artifact</text>\n";
    out << "<text x=\"530\" y=\"346\" font-size=\"12\">- expected trajectory vs actual trajectory</text>\n";
    out << "<text x=\"530\" y=\"366\" font-size=\"12\">- first divergence timestamp</text>\n";
    out << "<text x=\"530\" y=\"386\" font-size=\"12\">- timing-budget misses</text>\n";
    out << "<text x=\"530\" y=\"406\" font-size=\"12\">- root cause class</text>\n";
    out << "<text x=\"530\" y=\"426\" font-size=\"12\">- replay-based closed-loop debugging proof</text>\n";

    out << "</svg>\n";
}

}  // namespace dettrace
