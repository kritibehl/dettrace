#pragma once

#include <string>
#include <vector>

namespace dettrace {

struct ForensicsEvent {
    int seq = 0;
    std::string component;
    std::string action;
    std::string state;
    std::string detail;
    int timestamp_ms = 0;
};

struct InvariantBreak {
    std::string invariant_name;
    int event_index = -1;
    std::string evidence;
    double confidence = 0.0;
};

struct DivergenceReport {
    std::string scenario_name;
    int first_divergence_event = -1;
    std::string divergence_class;
    std::string expected_excerpt;
    std::string actual_excerpt;
    double confidence = 0.0;
};

struct RootCauseReport {
    std::string suspected_cause;
    double confidence = 0.0;
    std::vector<std::string> alternative_hypotheses;
    std::vector<std::string> affected_components;
    std::string likely_user_symptom;
    std::vector<std::string> key_evidence;
};

struct IncidentCard {
    std::string scenario_name;
    int first_divergence_event = -1;
    std::string suspected_cause;
    double confidence = 0.0;
    std::string symptom;
    std::string recommendation;
};

struct ScenarioBundle {
    std::string scenario_name;
    std::vector<ForensicsEvent> healthy;
    std::vector<ForensicsEvent> degraded;
    std::vector<ForensicsEvent> replayed;
    std::string scenario_notes;
    std::string fault_parameters;
};

std::vector<ScenarioBundle> build_forensics_scenario_pack();

void write_forensics_trace_jsonl(const std::string& path, const std::vector<ForensicsEvent>& events);
std::string render_trace_excerpt(const std::vector<ForensicsEvent>& events, int from, int count);

DivergenceReport classify_divergence(const ScenarioBundle& scenario);
std::vector<InvariantBreak> run_invariant_guided_replay(const ScenarioBundle& scenario);
std::string build_causal_chain_md(const ScenarioBundle& scenario,
                                  const DivergenceReport& divergence,
                                  const RootCauseReport& root);
RootCauseReport build_root_cause_report(const ScenarioBundle& scenario,
                                        const DivergenceReport& divergence,
                                        const std::vector<InvariantBreak>& invariant_breaks);
std::string build_incident_report_md(const ScenarioBundle& scenario,
                                     const DivergenceReport& divergence,
                                     const RootCauseReport& root,
                                     const std::vector<InvariantBreak>& invariant_breaks);
std::string build_scenario_summary_md(const std::vector<IncidentCard>& cards);
std::string build_invariant_breaks_md(const std::vector<InvariantBreak>& invariant_breaks);
std::string build_cluster_summary_json(const std::vector<DivergenceReport>& reports);
std::string build_propagation_view_md(const ScenarioBundle& scenario,
                                      const DivergenceReport& divergence,
                                      const RootCauseReport& root);
std::string build_incident_cards_md(const std::vector<IncidentCard>& cards);

}  // namespace dettrace
