#include "dettrace/incident_forensics.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <vector>

namespace fs = std::filesystem;

static void write_file(const std::string& path, const std::string& body) {
    std::ofstream out(path);
    out << body;
}

int main() {
    fs::create_directories("artifacts/traces");
    fs::create_directories("artifacts/reports");
    fs::create_directories("docs/case_studies");

    const auto scenarios = dettrace::build_forensics_scenario_pack();

    std::vector<dettrace::DivergenceReport> divergences;
    std::vector<dettrace::IncidentCard> cards;

    for (const auto& scenario : scenarios) {
        const std::string base = "artifacts/traces/" + scenario.scenario_name;
        fs::create_directories(base);

        dettrace::write_forensics_trace_jsonl(base + "/expected.jsonl", scenario.healthy);
        dettrace::write_forensics_trace_jsonl(base + "/degraded.jsonl", scenario.degraded);
        dettrace::write_forensics_trace_jsonl(base + "/replayed.jsonl", scenario.replayed);
        write_file(base + "/scenario_notes.md",
                   "# Scenario Notes\n\n- fault injection: " + scenario.fault_parameters + "\n- notes: " + scenario.scenario_notes + "\n");

        const auto divergence = dettrace::classify_divergence(scenario);
        const auto invariant_breaks = dettrace::run_invariant_guided_replay(scenario);
        const auto root = dettrace::build_root_cause_report(scenario, divergence, invariant_breaks);
        const auto causal = dettrace::build_causal_chain_md(scenario, divergence, root);
        const auto incident = dettrace::build_incident_report_md(scenario, divergence, root, invariant_breaks);
        const auto propagation = dettrace::build_propagation_view_md(scenario, divergence, root);

        divergences.push_back(divergence);
        cards.push_back({
            scenario.scenario_name,
            divergence.first_divergence_event,
            root.suspected_cause,
            root.confidence,
            root.likely_user_symptom,
            "inspect first divergence and invariant evidence before reacting to terminal symptom"
        });

        write_file("artifacts/reports/" + scenario.scenario_name + "_divergence_report.json",
                   "{\n"
                   "  \"scenario_name\": \"" + scenario.scenario_name + "\",\n"
                   "  \"first_divergence_event\": " + std::to_string(divergence.first_divergence_event) + ",\n"
                   "  \"divergence_class\": \"" + divergence.divergence_class + "\",\n"
                   "  \"expected_excerpt\": \"" + divergence.expected_excerpt + "\",\n"
                   "  \"actual_excerpt\": \"" + divergence.actual_excerpt + "\",\n"
                   "  \"confidence\": " + std::to_string(divergence.confidence) + "\n}\n");

        write_file("artifacts/reports/" + scenario.scenario_name + "_root_cause_report.json",
                   "{\n"
                   "  \"suspected_cause\": \"" + root.suspected_cause + "\",\n"
                   "  \"confidence\": " + std::to_string(root.confidence) + ",\n"
                   "  \"alternative_hypotheses\": " + ([&]{
                        std::ostringstream oss;
                        oss << "[";
                        for (size_t i = 0; i < root.alternative_hypotheses.size(); ++i) {
                            if (i) oss << ",";
                            oss << "\"" << root.alternative_hypotheses[i] << "\"";
                        }
                        oss << "]";
                        return oss.str();
                   })() + ",\n"
                   "  \"affected_components\": " + ([&]{
                        std::ostringstream oss;
                        oss << "[";
                        for (size_t i = 0; i < root.affected_components.size(); ++i) {
                            if (i) oss << ",";
                            oss << "\"" << root.affected_components[i] << "\"";
                        }
                        oss << "]";
                        return oss.str();
                   })() + ",\n"
                   "  \"likely_user_symptom\": \"" + root.likely_user_symptom + "\"\n}\n");

        write_file("artifacts/reports/" + scenario.scenario_name + "_incident_report.md", incident);
        write_file("artifacts/reports/" + scenario.scenario_name + "_causal_chain.md", causal);
        write_file("artifacts/reports/" + scenario.scenario_name + "_invariant_breaks.md",
                   dettrace::build_invariant_breaks_md(invariant_breaks));
        write_file("artifacts/reports/" + scenario.scenario_name + "_propagation_view.md", propagation);
    }

    write_file("artifacts/reports/scenario_summary.md", dettrace::build_scenario_summary_md(cards));
    write_file("artifacts/reports/incident_cards.md", dettrace::build_incident_cards_md(cards));
    write_file("artifacts/reports/cluster_summary.json", dettrace::build_cluster_summary_json(divergences));

    if (!scenarios.empty()) {
        write_file("docs/case_studies/retry_storm_divergence.md",
                   "# Retry Storm Case Study\n\n"
                   "This case study compares healthy vs degraded auth lookup behavior and shows how retry amplification becomes operator-visible failure.\n\n"
                   "## Healthy Trace Excerpt\n" +
                   dettrace::render_trace_excerpt(scenarios[1].healthy, 0, 4) +
                   "\n## Degraded Trace Excerpt\n" +
                   dettrace::render_trace_excerpt(scenarios[1].degraded, 0, 6) +
                   "\n## Why replay matters\n- logs often show aftermath\n- replay reveals drift onset\n- first divergence is more actionable than terminal symptom\n- causal reconstruction beats symptom-only debugging\n");
    }

    std::cout << "Incident forensics scenario pack complete\n";
    std::cout << "Generated elite artifacts under artifacts/traces and artifacts/reports\n";
    return 0;
}
