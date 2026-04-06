#include "dettrace/incident_forensics.hpp"

#include <cassert>
#include <string>
#include <vector>

int main() {
    const auto scenarios = dettrace::build_forensics_scenario_pack();
    assert(scenarios.size() == 6);

    bool saw_timeout_chain = false;
    bool saw_retry_amp = false;
    bool saw_recovery = false;

    std::vector<dettrace::DivergenceReport> reports;
    for (const auto& scenario : scenarios) {
        const auto divergence = dettrace::classify_divergence(scenario);
        const auto invariant_breaks = dettrace::run_invariant_guided_replay(scenario);
        const auto root = dettrace::build_root_cause_report(scenario, divergence, invariant_breaks);

        assert(divergence.first_divergence_event >= 0);
        assert(!divergence.divergence_class.empty());
        assert(root.confidence > 0.6);
        assert(!root.likely_user_symptom.empty());

        if (divergence.divergence_class == "timeout_chain") saw_timeout_chain = true;
        if (divergence.divergence_class == "retry_amplification") saw_retry_amp = true;
        if (divergence.divergence_class == "recovery misordering") saw_recovery = true;

        if (scenario.scenario_name == "duplicate_ack") {
            bool found = false;
            for (const auto& br : invariant_breaks) {
                if (br.invariant_name == "no duplicate completion without retry") found = true;
            }
            assert(found);
        }

        const auto causal = dettrace::build_causal_chain_md(scenario, divergence, root);
        assert(causal.find("What changed first") != std::string::npos);

        reports.push_back(divergence);
    }

    assert(saw_timeout_chain);
    assert(saw_retry_amp);
    assert(saw_recovery);

    const auto clusters = dettrace::build_cluster_summary_json(reports);
    assert(clusters.find("timing-related") != std::string::npos || clusters.find("retry-amplified") != std::string::npos);

    return 0;
}
