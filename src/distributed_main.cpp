#include "dettrace/distributed_trace.hpp"

#include <filesystem>
#include <fstream>
#include <iostream>

namespace fs = std::filesystem;

static void ensure_dirs() {
    fs::create_directories("artifacts");
    fs::create_directories("packs");
    fs::create_directories("reports");
    fs::create_directories("samples");
}

static void write_file(const std::string& path, const std::string& body) {
    std::ofstream out(path);
    out << body;
}

static void write_sample_otel_jsonl() {
    write_file("samples/otel_spans.jsonl",
R"({"trace_id":"trace-901","span_id":"otel-edge","parent_span_id":"","service":"edge-proxy","peer_service":"auth-service","kind":"CLIENT","status":"ok","failure_reason":"","retry_attempt":0,"latency_ms":8,"start_ms":5000,"cancelled":false}
{"trace_id":"trace-901","span_id":"otel-auth-1","parent_span_id":"otel-edge","service":"auth-service","peer_service":"token-db","kind":"SERVER","status":"network_error","failure_reason":"dns_failure","retry_attempt":0,"latency_ms":240,"start_ms":5240,"cancelled":false}
{"trace_id":"trace-901","span_id":"otel-edge","parent_span_id":"","service":"edge-proxy","peer_service":"auth-service","kind":"CLIENT","status":"retry","failure_reason":"retry_after_dns_failure","retry_attempt":1,"latency_ms":30,"start_ms":5270,"cancelled":false}
{"trace_id":"trace-901","span_id":"otel-auth-2","parent_span_id":"otel-edge","service":"auth-service","peer_service":"token-db","kind":"SERVER","status":"network_error","failure_reason":"transport_reset","retry_attempt":1,"latency_ms":285,"start_ms":5555,"cancelled":false}
{"trace_id":"trace-901","span_id":"otel-auth-3","parent_span_id":"otel-edge","service":"auth-service","peer_service":"token-db","kind":"SERVER","status":"timeout","failure_reason":"downstream_unavailable","retry_attempt":2,"latency_ms":910,"start_ms":6465,"cancelled":false}
)");
}

int main() {
    ensure_dirs();
    write_sample_otel_jsonl();

    const auto cascading = dettrace::build_cascading_timeout_pack();
    const auto retry_storm = dettrace::build_retry_storm_pack();
    const auto misordered = dettrace::build_misordered_recovery_pack();
    const auto failover = dettrace::build_failover_edge_pack();
    const auto otel_ingested = dettrace::ingest_otel_jsonl_as_events("samples/otel_spans.jsonl");

    dettrace::write_distributed_trace_jsonl("packs/cascading_timeouts.jsonl", cascading);
    dettrace::write_distributed_trace_jsonl("packs/retry_storm.jsonl", retry_storm);
    dettrace::write_distributed_trace_jsonl("packs/misordered_recovery.jsonl", misordered);
    dettrace::write_distributed_trace_jsonl("packs/failover_edge.jsonl", failover);
    dettrace::write_distributed_trace_jsonl("artifacts/otel_ingested_annotated.jsonl", otel_ingested);

    const auto baseline = dettrace::annotate_network_events(cascading);
    const auto candidate = dettrace::annotate_network_events(retry_storm);
    const auto replayed = dettrace::replay_distributed_incident(baseline);

    dettrace::write_distributed_trace_jsonl("artifacts/baseline_annotated.jsonl", baseline);
    dettrace::write_distributed_trace_jsonl("artifacts/candidate_annotated.jsonl", candidate);
    dettrace::write_distributed_trace_jsonl("artifacts/replayed_distributed.jsonl", replayed);

    write_file("reports/distributed_incident_report.json",
               dettrace::build_incident_report_json(baseline, candidate));
    write_file("reports/distributed_semantic_diff.json",
               dettrace::build_semantic_diff_json(baseline, candidate));

    std::cout << "Distributed incident demo complete\n";
    std::cout << "Generated sample OTEL input:\n";
    std::cout << "  samples/otel_spans.jsonl\n";
    std::cout << "Generated reports:\n";
    std::cout << "  reports/distributed_incident_report.json\n";
    std::cout << "  reports/distributed_semantic_diff.json\n";
    std::cout << "Generated artifact:\n";
    std::cout << "  artifacts/otel_ingested_annotated.jsonl\n";
    return 0;
}
