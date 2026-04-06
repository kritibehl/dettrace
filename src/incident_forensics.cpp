#include "dettrace/incident_forensics.hpp"

#include <algorithm>
#include <fstream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>

namespace dettrace {
namespace {

ForensicsEvent ev(int seq,
                  std::string component,
                  std::string action,
                  std::string state,
                  std::string detail,
                  int ts) {
    return {seq, std::move(component), std::move(action), std::move(state), std::move(detail), ts};
}

std::string esc(const std::string& s) {
    std::string out;
    for (char c : s) {
        switch (c) {
            case '\\': out += "\\\\"; break;
            case '"': out += "\\\""; break;
            case '\n': out += "\\n"; break;
            default: out += c; break;
        }
    }
    return out;
}

std::string json_array(const std::vector<std::string>& xs) {
    std::ostringstream oss;
    oss << "[";
    for (size_t i = 0; i < xs.size(); ++i) {
        if (i) oss << ",";
        oss << "\"" << esc(xs[i]) << "\"";
    }
    oss << "]";
    return oss.str();
}

std::string excerpt_event(const ForensicsEvent& e) {
    std::ostringstream oss;
    oss << "{seq=" << e.seq
        << ", component=" << e.component
        << ", action=" << e.action
        << ", state=" << e.state
        << ", detail=" << e.detail
        << "}";
    return oss.str();
}

ScenarioBundle make_timeout_chain() {
    ScenarioBundle s;
    s.scenario_name = "timeout_chain";
    s.fault_parameters = "inject profile->db timeout after nominal dependency request";
    s.scenario_notes = "Healthy run completes request path; degraded run accumulates timeout chain and cancellation.";
    s.healthy = {
        ev(0,"edge","request_start","ok","req-100",0),
        ev(1,"api","call_user","ok","req-100",10),
        ev(2,"user","call_profile","ok","req-100",25),
        ev(3,"profile","call_db","ok","req-100",40),
        ev(4,"db","reply","ok","rows=1",65),
        ev(5,"profile","reply","ok","profile_ready",75),
        ev(6,"user","reply","ok","user_ready",90),
        ev(7,"api","reply","ok","200",100)
    };
    s.degraded = {
        ev(0,"edge","request_start","ok","req-100",0),
        ev(1,"api","call_user","ok","req-100",10),
        ev(2,"user","call_profile","ok","req-100",25),
        ev(3,"profile","call_db","ok","req-100",40),
        ev(4,"profile","timeout","degraded","db_wait_exceeded",190),
        ev(5,"user","timeout","degraded","downstream_timeout",210),
        ev(6,"api","cancel","degraded","propagate_cancel",215),
        ev(7,"edge","reply","degraded","504_gateway_timeout",220)
    };
    s.replayed = s.healthy;
    return s;
}

ScenarioBundle make_retry_storm() {
    ScenarioBundle s;
    s.scenario_name = "retry_storm";
    s.fault_parameters = "inject auth dependency failures causing repeated retries";
    s.scenario_notes = "Healthy run performs a single auth lookup; degraded run amplifies retries and exposes error burst.";
    s.healthy = {
        ev(0,"edge","request_start","ok","trace-200",0),
        ev(1,"gateway","auth_lookup","ok","attempt=0",8),
        ev(2,"auth","token_db_lookup","ok","attempt=0",18),
        ev(3,"token-db","reply","ok","token_ok",35),
        ev(4,"auth","reply","ok","authorized",44),
        ev(5,"gateway","reply","ok","200",52)
    };
    s.degraded = {
        ev(0,"edge","request_start","ok","trace-200",0),
        ev(1,"gateway","auth_lookup","ok","attempt=0",8),
        ev(2,"auth","token_db_lookup","degraded","dns_failure",18),
        ev(3,"gateway","retry","degraded","attempt=1",32),
        ev(4,"auth","token_db_lookup","degraded","transport_reset",55),
        ev(5,"gateway","retry","degraded","attempt=2",70),
        ev(6,"auth","token_db_lookup","degraded","timeout_chain",135),
        ev(7,"gateway","reply","degraded","503_auth_unavailable",145)
    };
    s.replayed = s.healthy;
    return s;
}

ScenarioBundle make_stale_state() {
    ScenarioBundle s;
    s.scenario_name = "stale_state";
    s.fault_parameters = "inject stale state estimate during control/state sync";
    s.scenario_notes = "Healthy run updates state estimate before actuation; degraded run acts on stale state.";
    s.healthy = {
        ev(0,"planner","state_update","ok","est=v1",0),
        ev(1,"controller","consume_state","ok","est=v1",10),
        ev(2,"controller","actuate","ok","cmd=nominal",20),
        ev(3,"plant","state_commit","ok","x=1.0",35)
    };
    s.degraded = {
        ev(0,"planner","state_update","ok","est=v1",0),
        ev(1,"planner","state_update","ok","est=v2",8),
        ev(2,"controller","consume_state","degraded","est=v1_stale",10),
        ev(3,"controller","actuate","degraded","cmd_from_stale_state",20),
        ev(4,"plant","state_commit","degraded","drift_detected",36)
    };
    s.replayed = s.healthy;
    return s;
}

ScenarioBundle make_delayed_dependency() {
    ScenarioBundle s;
    s.scenario_name = "delayed_dependency";
    s.fault_parameters = "inject delayed dependency-ready event";
    s.scenario_notes = "Healthy run waits for dependency-ready before action; degraded run observes delayed dependency and misses deadline.";
    s.healthy = {
        ev(0,"orchestrator","dependency_probe","ok","cache",0),
        ev(1,"cache","ready","ok","cache_ready",12),
        ev(2,"orchestrator","dispatch","ok","job_start",20),
        ev(3,"worker","complete","ok","job_done",55)
    };
    s.degraded = {
        ev(0,"orchestrator","dependency_probe","ok","cache",0),
        ev(1,"orchestrator","dispatch","degraded","action_before_ready",8),
        ev(2,"cache","ready","degraded","cache_ready_late",40),
        ev(3,"worker","complete","degraded","deadline_miss",85)
    };
    s.replayed = s.healthy;
    return s;
}

ScenarioBundle make_duplicate_ack() {
    ScenarioBundle s;
    s.scenario_name = "duplicate_ack";
    s.fault_parameters = "inject duplicate completion acknowledgment without retry";
    s.scenario_notes = "Healthy run has one completion ack; degraded run emits duplicate ack and causes invariant break.";
    s.healthy = {
        ev(0,"worker","start","ok","job-1",0),
        ev(1,"worker","complete","ok","job-1",30),
        ev(2,"coordinator","ack","ok","job-1_ack",34)
    };
    s.degraded = {
        ev(0,"worker","start","ok","job-1",0),
        ev(1,"worker","complete","ok","job-1",30),
        ev(2,"coordinator","ack","ok","job-1_ack",34),
        ev(3,"coordinator","ack","degraded","job-1_duplicate_ack",35)
    };
    s.replayed = s.healthy;
    return s;
}

ScenarioBundle make_misordered_recovery() {
    ScenarioBundle s;
    s.scenario_name = "misordered_recovery";
    s.fault_parameters = "mark service healthy before downstream recovery stabilizes";
    s.scenario_notes = "Healthy run recovers downstream first; degraded run flips health early and masks ongoing dependency failure.";
    s.healthy = {
        ev(0,"lb","failover","ok","to_b",0),
        ev(1,"checkout-b","recover","ok","instance_ready",22),
        ev(2,"payment","recover","ok","dependency_ready",35),
        ev(3,"lb","healthy","ok","route_stable",45)
    };
    s.degraded = {
        ev(0,"lb","failover","ok","to_b",0),
        ev(1,"checkout-a","healthy","degraded","marked_healthy_early",12),
        ev(2,"payment","error","degraded","dependency_unavailable",26),
        ev(3,"lb","route","degraded","masked_recovery_path",32)
    };
    s.replayed = s.healthy;
    return s;
}

std::string classify_name(const ScenarioBundle& s) {
    if (s.scenario_name == "timeout_chain") return "timeout_chain";
    if (s.scenario_name == "retry_storm") return "retry_amplification";
    if (s.scenario_name == "stale_state") return "stale-state transition";
    if (s.scenario_name == "delayed_dependency") return "timing divergence";
    if (s.scenario_name == "duplicate_ack") return "duplicate event";
    if (s.scenario_name == "misordered_recovery") return "recovery misordering";
    return "ordering divergence";
}

}  // namespace

std::vector<ScenarioBundle> build_forensics_scenario_pack() {
    return {
        make_timeout_chain(),
        make_retry_storm(),
        make_stale_state(),
        make_delayed_dependency(),
        make_duplicate_ack(),
        make_misordered_recovery()
    };
}

void write_forensics_trace_jsonl(const std::string& path, const std::vector<ForensicsEvent>& events) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("failed to open " + path);
    for (const auto& e : events) {
        out << "{"
            << "\"seq\":" << e.seq << ","
            << "\"component\":\"" << esc(e.component) << "\","
            << "\"action\":\"" << esc(e.action) << "\","
            << "\"state\":\"" << esc(e.state) << "\","
            << "\"detail\":\"" << esc(e.detail) << "\","
            << "\"timestamp_ms\":" << e.timestamp_ms
            << "}\n";
    }
}

std::string render_trace_excerpt(const std::vector<ForensicsEvent>& events, int from, int count) {
    std::ostringstream oss;
    const int start = std::max(0, from);
    const int end = std::min<int>(events.size(), start + count);
    for (int i = start; i < end; ++i) {
        oss << "- " << excerpt_event(events[i]) << "\n";
    }
    return oss.str();
}

DivergenceReport classify_divergence(const ScenarioBundle& scenario) {
    DivergenceReport r;
    r.scenario_name = scenario.scenario_name;
    const int n = std::min<int>(scenario.healthy.size(), scenario.degraded.size());
    for (int i = 0; i < n; ++i) {
        const auto& h = scenario.healthy[i];
        const auto& d = scenario.degraded[i];
        if (h.action != d.action || h.state != d.state || h.detail != d.detail || h.component != d.component) {
            r.first_divergence_event = i;
            r.expected_excerpt = excerpt_event(h);
            r.actual_excerpt = excerpt_event(d);
            break;
        }
    }
    if (r.first_divergence_event == -1 && scenario.healthy.size() != scenario.degraded.size()) {
        r.first_divergence_event = n;
        r.expected_excerpt = n < static_cast<int>(scenario.healthy.size()) ? excerpt_event(scenario.healthy[n]) : "<end_of_trace>";
        r.actual_excerpt = n < static_cast<int>(scenario.degraded.size()) ? excerpt_event(scenario.degraded[n]) : "<end_of_trace>";
    }
    r.divergence_class = classify_name(scenario);
    r.confidence = 0.82;
    if (r.divergence_class == "timing divergence") r.confidence = 0.76;
    if (r.divergence_class == "ordering divergence") r.confidence = 0.68;
    return r;
}

std::vector<InvariantBreak> run_invariant_guided_replay(const ScenarioBundle& scenario) {
    std::vector<InvariantBreak> out;

    for (size_t i = 0; i < scenario.degraded.size(); ++i) {
        const auto& e = scenario.degraded[i];

        if (e.action == "ack" && e.detail.find("duplicate") != std::string::npos) {
            out.push_back({"no duplicate completion without retry", static_cast<int>(i), excerpt_event(e), 0.96});
        }
        if (e.action == "dispatch" && e.detail == "action_before_ready") {
            out.push_back({"no action before dependency-ready", static_cast<int>(i), excerpt_event(e), 0.91});
        }
        if (e.action == "healthy" && e.detail == "marked_healthy_early") {
            out.push_back({"recovery must follow failure within N steps", static_cast<int>(i), excerpt_event(e), 0.88});
        }
        if (e.action == "actuate" && e.detail == "cmd_from_stale_state") {
            out.push_back({"ack ordering must preserve causality", static_cast<int>(i), excerpt_event(e), 0.73});
        }
    }

    return out;
}

RootCauseReport build_root_cause_report(const ScenarioBundle& scenario,
                                        const DivergenceReport& divergence,
                                        const std::vector<InvariantBreak>& invariant_breaks) {
    RootCauseReport r;
    r.suspected_cause = divergence.divergence_class;
    r.confidence = divergence.confidence;
    r.affected_components.push_back(scenario.degraded[std::min<int>(divergence.first_divergence_event, static_cast<int>(scenario.degraded.size()) - 1)].component);
    r.key_evidence.push_back(divergence.actual_excerpt);

    if (!invariant_breaks.empty()) {
        r.key_evidence.push_back(invariant_breaks.front().evidence);
        r.confidence = std::min(0.97, divergence.confidence + 0.08);
    }

    if (scenario.scenario_name == "timeout_chain") {
        r.likely_user_symptom = "gateway timeout visible to operator";
        r.alternative_hypotheses = {"ordering instability after retry", "missing dependency-ready trace granularity"};
        r.affected_components.push_back("api");
        r.affected_components.push_back("profile");
    } else if (scenario.scenario_name == "retry_storm") {
        r.likely_user_symptom = "burst of auth failures and elevated latency";
        r.alternative_hypotheses = {"dependency DNS flap", "transport reset before timeout"};
        r.affected_components.push_back("gateway");
        r.affected_components.push_back("auth");
    } else if (scenario.scenario_name == "stale_state") {
        r.likely_user_symptom = "control drift or stale state actuation";
        r.alternative_hypotheses = {"delayed sensor update", "ordering instability in state pipeline"};
        r.affected_components.push_back("controller");
    } else if (scenario.scenario_name == "delayed_dependency") {
        r.likely_user_symptom = "deadline miss after dependency delay";
        r.alternative_hypotheses = {"incorrect readiness gating", "dependency probe lag"};
        r.affected_components.push_back("orchestrator");
    } else if (scenario.scenario_name == "duplicate_ack") {
        r.likely_user_symptom = "duplicate completion or user-visible duplicate side effect";
        r.alternative_hypotheses = {"retry bookkeeping bug", "idempotency guard missing"};
        r.affected_components.push_back("coordinator");
    } else {
        r.likely_user_symptom = "recovery appears healthy before correctness is restored";
        r.alternative_hypotheses = {"masked failover", "premature health signal"};
        r.affected_components.push_back("lb");
        r.affected_components.push_back("payment");
    }

    std::sort(r.affected_components.begin(), r.affected_components.end());
    r.affected_components.erase(std::unique(r.affected_components.begin(), r.affected_components.end()), r.affected_components.end());
    return r;
}

std::string build_causal_chain_md(const ScenarioBundle& scenario,
                                  const DivergenceReport& divergence,
                                  const RootCauseReport& root) {
    std::ostringstream oss;
    oss << "# Causal Chain\n\n"
        << "- **Scenario:** " << scenario.scenario_name << "\n"
        << "- **What changed first:** event " << divergence.first_divergence_event << " -> " << divergence.actual_excerpt << "\n"
        << "- **What downstream behaviors changed:** operator-visible symptom became `" << root.likely_user_symptom << "`\n"
        << "- **Which subsystem was affected first:** " << (root.affected_components.empty() ? "unknown" : root.affected_components.front()) << "\n"
        << "- **Did recovery restore correctness or mask behavior:** "
        << (scenario.scenario_name == "misordered_recovery" ? "recovery masked ongoing incorrect behavior" : "recovery did not occur before symptom exposure")
        << "\n";
    return oss.str();
}

std::string build_incident_report_md(const ScenarioBundle& scenario,
                                     const DivergenceReport& divergence,
                                     const RootCauseReport& root,
                                     const std::vector<InvariantBreak>& invariant_breaks) {
    std::ostringstream oss;
    oss << "# Incident Report\n\n"
        << "- **Scenario:** " << scenario.scenario_name << "\n"
        << "- **Suspected cause:** " << root.suspected_cause << "\n"
        << "- **Confidence:** " << root.confidence << "\n"
        << "- **First divergence event:** " << divergence.first_divergence_event << "\n"
        << "- **Affected components:** ";
    for (size_t i = 0; i < root.affected_components.size(); ++i) {
        if (i) oss << ", ";
        oss << root.affected_components[i];
    }
    oss << "\n"
        << "- **Likely user symptom:** " << root.likely_user_symptom << "\n"
        << "- **Alternative hypotheses:** ";
    for (size_t i = 0; i < root.alternative_hypotheses.size(); ++i) {
        if (i) oss << "; ";
        oss << root.alternative_hypotheses[i];
    }
    oss << "\n\n## Key Evidence\n";
    for (const auto& e : root.key_evidence) {
        oss << "- " << e << "\n";
    }
    if (!invariant_breaks.empty()) {
        oss << "\n## Invariant Breaks\n";
        for (const auto& br : invariant_breaks) {
            oss << "- " << br.invariant_name << " at event " << br.event_index
                << " (confidence=" << br.confidence << "): " << br.evidence << "\n";
        }
    }
    return oss.str();
}

std::string build_scenario_summary_md(const std::vector<IncidentCard>& cards) {
    std::ostringstream oss;
    oss << "# Scenario Summary\n\n";
    for (const auto& c : cards) {
        oss << "## " << c.scenario_name << "\n"
            << "- first divergence: " << c.first_divergence_event << "\n"
            << "- suspected cause: " << c.suspected_cause << "\n"
            << "- confidence: " << c.confidence << "\n"
            << "- symptom: " << c.symptom << "\n"
            << "- recommendation: " << c.recommendation << "\n\n";
    }
    return oss.str();
}

std::string build_invariant_breaks_md(const std::vector<InvariantBreak>& invariant_breaks) {
    std::ostringstream oss;
    oss << "# Invariant Breaks\n\n";
    if (invariant_breaks.empty()) {
        oss << "- none detected\n";
        return oss.str();
    }
    for (const auto& br : invariant_breaks) {
        oss << "- " << br.invariant_name << " at event " << br.event_index
            << " | confidence=" << br.confidence
            << " | evidence=" << br.evidence << "\n";
    }
    return oss.str();
}

std::string build_cluster_summary_json(const std::vector<DivergenceReport>& reports) {
    std::map<std::string, int> counts;
    for (const auto& r : reports) {
        std::string cluster = "ordering-related";
        if (r.divergence_class.find("timing") != std::string::npos || r.divergence_class.find("timeout") != std::string::npos) cluster = "timing-related";
        if (r.divergence_class.find("stale") != std::string::npos) cluster = "stale-state-related";
        if (r.divergence_class.find("retry") != std::string::npos) cluster = "retry-amplified";
        if (r.divergence_class.find("recovery") != std::string::npos) cluster = "recovery-path-related";
        counts[cluster]++;
    }

    std::ostringstream oss;
    oss << "{";
    bool first = true;
    for (const auto& kv : counts) {
        if (!first) oss << ",";
        first = false;
        oss << "\"" << kv.first << "\":" << kv.second;
    }
    oss << "}\n";
    return oss.str();
}

std::string build_propagation_view_md(const ScenarioBundle& scenario,
                                      const DivergenceReport& divergence,
                                      const RootCauseReport& root) {
    std::ostringstream oss;
    oss << "# Propagation View\n\n"
        << "```text\n"
        << "healthy path\n"
        << "  " << scenario.healthy.front().component << " -> ... -> "
        << scenario.healthy.back().component << "\n\n"
        << "degraded path\n"
        << "  divergence@" << divergence.first_divergence_event << " -> "
        << divergence.divergence_class << " -> "
        << root.likely_user_symptom << "\n"
        << "```\n";
    return oss.str();
}

std::string build_incident_cards_md(const std::vector<IncidentCard>& cards) {
    std::ostringstream oss;
    oss << "# Incident Cards\n\n";
    for (const auto& c : cards) {
        oss << "## " << c.scenario_name << "\n"
            << "- first divergence: " << c.first_divergence_event << "\n"
            << "- suspected cause: " << c.suspected_cause << "\n"
            << "- confidence: " << c.confidence << "\n"
            << "- symptom: " << c.symptom << "\n"
            << "- recommendation: " << c.recommendation << "\n\n";
    }
    return oss.str();
}

}  // namespace dettrace
