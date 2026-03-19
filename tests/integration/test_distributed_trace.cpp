#include "dettrace/distributed_trace.hpp"

#include <cassert>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>

namespace fs = std::filesystem;

static std::string slurp(const std::string& path) {
    std::ifstream in(path);
    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

int main() {
    const int rc = std::system("./dettrace_distributed > /tmp/dettrace_distributed_test_output.txt 2>&1");
    assert(rc == 0);

    assert(fs::exists("samples/otel_spans.jsonl"));
    assert(fs::exists("artifacts/otel_ingested_annotated.jsonl"));
    assert(fs::exists("reports/distributed_incident_report.json"));
    assert(fs::exists("reports/distributed_semantic_diff.json"));

    const auto otel = dettrace::read_distributed_trace_jsonl("artifacts/otel_ingested_annotated.jsonl");
    assert(!otel.empty());

    bool saw_dns = false;
    bool saw_retry_burst = false;
    for (const auto& e : otel) {
        for (const auto& a : e.annotations) {
            if (a == "dns_failure") saw_dns = true;
            if (a == "retry_burst") saw_retry_burst = true;
        }
    }
    assert(saw_dns);
    assert(saw_retry_burst);

    const auto baseline = dettrace::annotate_network_events(dettrace::build_cascading_timeout_pack());
    const auto candidate = dettrace::annotate_network_events(dettrace::build_retry_storm_pack());

    const auto timeline = dettrace::correlate_incident_timeline(candidate, 5200, 1200);
    assert(timeline.deploy_correlated);
    assert(timeline.error_burst_count >= 2);

    const auto blast = dettrace::infer_blast_radius(candidate);
    assert(!blast.root_service.empty());
    assert(blast.retry_events >= 2);

    const auto diff = dettrace::build_semantic_diff_json(baseline, candidate);
    assert(diff.find("retry_delta") != std::string::npos);
    assert(diff.find("candidate_first_failure_reason") != std::string::npos);

    const auto report = slurp("reports/distributed_incident_report.json");
    assert(report.find("timeline_correlation") != std::string::npos);
    assert(report.find("blast_radius") != std::string::npos);

    return 0;
}
