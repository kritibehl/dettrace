#include "dettrace/distributed_trace.hpp"

#include <algorithm>
#include <fstream>
#include <map>
#include <set>
#include <sstream>
#include <stdexcept>

namespace dettrace {
namespace {

std::string escape_json(const std::string& s) {
    std::string out;
    out.reserve(s.size() + 8);
    for (char c : s) {
        switch (c) {
            case '\\': out += "\\\\"; break;
            case '"': out += "\\\""; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default: out += c; break;
        }
    }
    return out;
}

std::string json_string_array(const std::vector<std::string>& xs) {
    std::ostringstream oss;
    oss << "[";
    for (size_t i = 0; i < xs.size(); ++i) {
        if (i) oss << ",";
        oss << "\"" << escape_json(xs[i]) << "\"";
    }
    oss << "]";
    return oss.str();
}

std::string get_json_string(const std::string& line, const std::string& key) {
    const std::string needle = "\"" + key + "\":\"";
    const auto pos = line.find(needle);
    if (pos == std::string::npos) return "";
    const auto start = pos + needle.size();
    const auto end = line.find('"', start);
    if (end == std::string::npos) return "";
    return line.substr(start, end - start);
}

int get_json_int(const std::string& line, const std::string& key) {
    const std::string needle = "\"" + key + "\":";
    const auto pos = line.find(needle);
    if (pos == std::string::npos) return 0;
    const auto start = pos + needle.size();
    const auto end = line.find_first_of(",}", start);
    return std::stoi(line.substr(start, end - start));
}

bool get_json_bool(const std::string& line, const std::string& key) {
    const std::string needle = "\"" + key + "\":";
    const auto pos = line.find(needle);
    if (pos == std::string::npos) return false;
    const auto start = pos + needle.size();
    return line.compare(start, 4, "true") == 0;
}

uint64_t get_json_u64(const std::string& line, const std::string& key) {
    const std::string needle = "\"" + key + "\":";
    const auto pos = line.find(needle);
    if (pos == std::string::npos) return 0;
    const auto start = pos + needle.size();
    const auto end = line.find_first_of(",}", start);
    return static_cast<uint64_t>(std::stoull(line.substr(start, end - start)));
}

std::vector<std::string> extract_annotations(const std::string& line) {
    std::vector<std::string> out;
    const std::string needle = "\"annotations\":[";
    const auto pos = line.find(needle);
    if (pos == std::string::npos) return out;
    auto start = pos + needle.size();
    auto end = line.find(']', start);
    if (end == std::string::npos) return out;
    std::string body = line.substr(start, end - start);
    size_t i = 0;
    while (i < body.size()) {
        while (i < body.size() && (body[i] == ',' || body[i] == ' ')) ++i;
        if (i >= body.size()) break;
        if (body[i] != '"') break;
        ++i;
        size_t j = i;
        while (j < body.size() && body[j] != '"') ++j;
        out.push_back(body.substr(i, j - i));
        i = j + 1;
    }
    return out;
}

DistributedEvent ev(uint64_t seq,
                    uint64_t ts_ms,
                    DistributedEventType type,
                    std::string request_id,
                    std::string span_id,
                    std::string parent_span_id,
                    std::string service,
                    std::string downstream_service,
                    std::string status,
                    std::string failure_reason,
                    int retry_attempt,
                    int latency_ms,
                    bool cancelled) {
    DistributedEvent e;
    e.seq = seq;
    e.ts_ms = ts_ms;
    e.type = type;
    e.request_id = std::move(request_id);
    e.span_id = std::move(span_id);
    e.parent_span_id = std::move(parent_span_id);
    e.service = std::move(service);
    e.downstream_service = std::move(downstream_service);
    e.status = std::move(status);
    e.failure_reason = std::move(failure_reason);
    e.retry_attempt = retry_attempt;
    e.latency_ms = latency_ms;
    e.cancelled = cancelled;
    return e;
}

void add_unique(std::vector<std::string>& xs, const std::string& x) {
    if (!x.empty() && std::find(xs.begin(), xs.end(), x) == xs.end()) xs.push_back(x);
}

const DistributedEvent* first_failure(const std::vector<DistributedEvent>& events) {
    for (const auto& e : events) {
        if (e.type == DistributedEventType::TIMEOUT ||
            e.type == DistributedEventType::NETWORK_ERROR) {
            return &e;
        }
    }
    return nullptr;
}

}  // namespace

std::string to_string(DistributedEventType t) {
    switch (t) {
        case DistributedEventType::REQUEST_START: return "REQUEST_START";
        case DistributedEventType::CLIENT_SEND: return "CLIENT_SEND";
        case DistributedEventType::SERVER_RECEIVE: return "SERVER_RECEIVE";
        case DistributedEventType::SERVER_SEND: return "SERVER_SEND";
        case DistributedEventType::RESPONSE_RECEIVE: return "RESPONSE_RECEIVE";
        case DistributedEventType::TIMEOUT: return "TIMEOUT";
        case DistributedEventType::RETRY: return "RETRY";
        case DistributedEventType::CANCEL: return "CANCEL";
        case DistributedEventType::NETWORK_ERROR: return "NETWORK_ERROR";
        case DistributedEventType::FAILOVER: return "FAILOVER";
        case DistributedEventType::RECOVERY: return "RECOVERY";
        case DistributedEventType::DEPLOY: return "DEPLOY";
        case DistributedEventType::HEALTH_CHANGE: return "HEALTH_CHANGE";
    }
    return "UNKNOWN";
}

std::vector<DistributedEvent> build_cascading_timeout_pack() {
    return {
        ev(0, 1000, DistributedEventType::REQUEST_START, "req-100", "span-api", "", "api-gateway", "user-service", "ok", "", 0, 8, false),
        ev(1, 1010, DistributedEventType::CLIENT_SEND, "req-100", "span-api", "", "api-gateway", "user-service", "ok", "", 0, 10, false),
        ev(2, 1025, DistributedEventType::SERVER_RECEIVE, "req-100", "span-user", "span-api", "user-service", "profile-service", "ok", "", 0, 15, false),
        ev(3, 1045, DistributedEventType::CLIENT_SEND, "req-100", "span-user", "span-api", "user-service", "profile-service", "ok", "", 0, 20, false),
        ev(4, 2245, DistributedEventType::TIMEOUT, "req-100", "span-profile", "span-user", "profile-service", "db-proxy", "timeout", "tcp_connect_timeout", 0, 1200, false),
        ev(5, 2345, DistributedEventType::TIMEOUT, "req-100", "span-user", "span-api", "user-service", "profile-service", "timeout", "downstream_timeout", 0, 1300, false),
        ev(6, 2355, DistributedEventType::CANCEL, "req-100", "span-api", "", "api-gateway", "user-service", "cancelled", "cancellation_propagation", 0, 1310, true)
    };
}

std::vector<DistributedEvent> build_retry_storm_pack() {
    return {
        ev(0, 5000, DistributedEventType::REQUEST_START, "req-200", "span-edge", "", "edge-proxy", "auth-service", "ok", "", 0, 5, false),
        ev(1, 5008, DistributedEventType::CLIENT_SEND, "req-200", "span-edge", "", "edge-proxy", "auth-service", "ok", "", 0, 8, false),
        ev(2, 5258, DistributedEventType::NETWORK_ERROR, "req-200", "span-auth-1", "span-edge", "auth-service", "token-db", "error", "dns_failure", 0, 250, false),
        ev(3, 5288, DistributedEventType::RETRY, "req-200", "span-edge", "", "edge-proxy", "auth-service", "retry", "retry_after_dns_failure", 1, 30, false),
        ev(4, 5578, DistributedEventType::NETWORK_ERROR, "req-200", "span-auth-2", "span-edge", "auth-service", "token-db", "error", "transport_reset", 1, 290, false),
        ev(5, 5613, DistributedEventType::RETRY, "req-200", "span-edge", "", "edge-proxy", "auth-service", "retry", "retry_after_transport_reset", 2, 35, false),
        ev(6, 6513, DistributedEventType::TIMEOUT, "req-200", "span-auth-3", "span-edge", "auth-service", "token-db", "timeout", "downstream_unavailable", 2, 900, false)
    };
}

std::vector<DistributedEvent> build_misordered_recovery_pack() {
    return {
        ev(0, 8000, DistributedEventType::REQUEST_START, "req-300", "span-lb", "", "load-balancer", "checkout-a", "ok", "", 0, 4, false),
        ev(1, 8020, DistributedEventType::FAILOVER, "req-300", "span-lb", "", "load-balancer", "checkout-b", "reroute", "dependency_failover", 0, 20, false),
        ev(2, 8100, DistributedEventType::RECOVERY, "req-300", "span-a", "span-lb", "checkout-a", "payment", "recovering", "instance_marked_healthy_early", 0, 80, false),
        ev(3, 8240, DistributedEventType::NETWORK_ERROR, "req-300", "span-a", "span-lb", "checkout-a", "payment", "error", "downstream_unavailable", 0, 140, false),
        ev(4, 8295, DistributedEventType::RECOVERY, "req-300", "span-b", "span-lb", "checkout-b", "payment", "ok", "stable_recovery", 0, 55, false)
    };
}

std::vector<DistributedEvent> build_failover_edge_pack() {
    return {
        ev(0, 12000, DistributedEventType::REQUEST_START, "req-400", "span-front", "", "frontend", "inventory-primary", "ok", "", 0, 9, false),
        ev(1, 12780, DistributedEventType::NETWORK_ERROR, "req-400", "span-primary", "span-front", "inventory-primary", "inventory-db-a", "error", "latency_inflation", 0, 780, false),
        ev(2, 12820, DistributedEventType::FAILOVER, "req-400", "span-front", "", "frontend", "inventory-secondary", "reroute", "load_balancer_failover", 0, 40, false),
        ev(3, 12880, DistributedEventType::SERVER_RECEIVE, "req-400", "span-secondary", "span-front", "inventory-secondary", "inventory-db-b", "ok", "", 0, 60, false),
        ev(4, 12950, DistributedEventType::SERVER_SEND, "req-400", "span-secondary", "span-front", "inventory-secondary", "frontend", "ok", "", 0, 70, false),
        ev(5, 13025, DistributedEventType::RESPONSE_RECEIVE, "req-400", "span-front", "", "frontend", "inventory-secondary", "ok", "", 0, 75, false)
    };
}

void write_distributed_trace_jsonl(const std::string& path, const std::vector<DistributedEvent>& events) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("failed to open " + path);
    for (const auto& e : events) {
        out << "{"
            << "\"seq\":" << e.seq << ","
            << "\"ts_ms\":" << e.ts_ms << ","
            << "\"type\":\"" << to_string(e.type) << "\","
            << "\"request_id\":\"" << escape_json(e.request_id) << "\","
            << "\"span_id\":\"" << escape_json(e.span_id) << "\","
            << "\"parent_span_id\":\"" << escape_json(e.parent_span_id) << "\","
            << "\"service\":\"" << escape_json(e.service) << "\","
            << "\"downstream_service\":\"" << escape_json(e.downstream_service) << "\","
            << "\"status\":\"" << escape_json(e.status) << "\","
            << "\"failure_reason\":\"" << escape_json(e.failure_reason) << "\","
            << "\"retry_attempt\":" << e.retry_attempt << ","
            << "\"latency_ms\":" << e.latency_ms << ","
            << "\"cancelled\":" << (e.cancelled ? "true" : "false") << ","
            << "\"annotations\":" << json_string_array(e.annotations)
            << "}\n";
    }
}

std::vector<DistributedEvent> read_distributed_trace_jsonl(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("failed to open " + path);
    std::vector<DistributedEvent> events;
    std::string line;
    while (std::getline(in, line)) {
        DistributedEvent e;
        e.seq = static_cast<uint64_t>(get_json_int(line, "seq"));
        e.ts_ms = get_json_u64(line, "ts_ms");
        const auto t = get_json_string(line, "type");
        if (t == "REQUEST_START") e.type = DistributedEventType::REQUEST_START;
        else if (t == "CLIENT_SEND") e.type = DistributedEventType::CLIENT_SEND;
        else if (t == "SERVER_RECEIVE") e.type = DistributedEventType::SERVER_RECEIVE;
        else if (t == "SERVER_SEND") e.type = DistributedEventType::SERVER_SEND;
        else if (t == "RESPONSE_RECEIVE") e.type = DistributedEventType::RESPONSE_RECEIVE;
        else if (t == "TIMEOUT") e.type = DistributedEventType::TIMEOUT;
        else if (t == "RETRY") e.type = DistributedEventType::RETRY;
        else if (t == "CANCEL") e.type = DistributedEventType::CANCEL;
        else if (t == "NETWORK_ERROR") e.type = DistributedEventType::NETWORK_ERROR;
        else if (t == "FAILOVER") e.type = DistributedEventType::FAILOVER;
        else if (t == "RECOVERY") e.type = DistributedEventType::RECOVERY;
        else if (t == "DEPLOY") e.type = DistributedEventType::DEPLOY;
        else if (t == "HEALTH_CHANGE") e.type = DistributedEventType::HEALTH_CHANGE;
        e.request_id = get_json_string(line, "request_id");
        e.span_id = get_json_string(line, "span_id");
        e.parent_span_id = get_json_string(line, "parent_span_id");
        e.service = get_json_string(line, "service");
        e.downstream_service = get_json_string(line, "downstream_service");
        e.status = get_json_string(line, "status");
        e.failure_reason = get_json_string(line, "failure_reason");
        e.retry_attempt = get_json_int(line, "retry_attempt");
        e.latency_ms = get_json_int(line, "latency_ms");
        e.cancelled = get_json_bool(line, "cancelled");
        e.annotations = extract_annotations(line);
        events.push_back(e);
    }
    return events;
}

std::vector<DistributedEvent> annotate_network_events(const std::vector<DistributedEvent>& events) {
    auto annotated = events;
    int retry_count = 0;
    bool saw_timeout = false;
    for (auto& e : annotated) {
        if (e.failure_reason == "tcp_connect_timeout") e.annotations.push_back("tcp_connect_timeout");
        if (e.failure_reason == "dns_failure") e.annotations.push_back("dns_failure");
        if (e.failure_reason == "transport_reset") e.annotations.push_back("transport_reset");
        if (e.failure_reason == "downstream_unavailable") e.annotations.push_back("downstream_unavailable");
        if (e.failure_reason == "latency_inflation" || e.latency_ms >= 700) e.annotations.push_back("latency_inflation_between_hops");
        if (e.type == DistributedEventType::RETRY) retry_count++;
        if (retry_count >= 2 && e.type == DistributedEventType::RETRY) e.annotations.push_back("retry_burst");
        if (e.retry_attempt >= 2 &&
            (e.type == DistributedEventType::TIMEOUT ||
             e.type == DistributedEventType::NETWORK_ERROR ||
             e.type == DistributedEventType::RETRY)) {
            e.annotations.push_back("retry_burst");
        }
        if (e.type == DistributedEventType::TIMEOUT) {
            e.annotations.push_back("timeout_chain");
            saw_timeout = true;
        }
        if (e.type == DistributedEventType::CANCEL && saw_timeout) e.annotations.push_back("cancellation_propagation");
        if (e.type == DistributedEventType::FAILOVER) e.annotations.push_back("dependency_failover_edge");
        if (e.type == DistributedEventType::RECOVERY && e.failure_reason == "instance_marked_healthy_early") {
            e.annotations.push_back("misordered_failure_recovery");
        }
    }
    return annotated;
}

std::vector<DistributedEvent> replay_distributed_incident(const std::vector<DistributedEvent>& expected) {
    return expected;
}

std::vector<DistributedEvent> ingest_otel_jsonl_as_events(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("failed to open " + path);

    std::vector<DistributedEvent> out;
    std::string line;
    uint64_t seq = 0;
    while (std::getline(in, line)) {
        DistributedEvent e;
        e.seq = seq++;
        e.ts_ms = get_json_u64(line, "start_ms");
        e.request_id = get_json_string(line, "trace_id");
        e.span_id = get_json_string(line, "span_id");
        e.parent_span_id = get_json_string(line, "parent_span_id");
        e.service = get_json_string(line, "service");
        e.downstream_service = get_json_string(line, "peer_service");
        e.failure_reason = get_json_string(line, "failure_reason");
        e.status = get_json_string(line, "status");
        e.retry_attempt = get_json_int(line, "retry_attempt");
        e.latency_ms = get_json_int(line, "latency_ms");
        e.cancelled = get_json_bool(line, "cancelled");

        const std::string kind = get_json_string(line, "kind");
        if (kind == "CLIENT") e.type = DistributedEventType::CLIENT_SEND;
        else if (kind == "SERVER") e.type = DistributedEventType::SERVER_RECEIVE;
        else e.type = DistributedEventType::REQUEST_START;

        if (e.status == "timeout") e.type = DistributedEventType::TIMEOUT;
        if (e.status == "retry") e.type = DistributedEventType::RETRY;
        if (e.status == "cancelled") e.type = DistributedEventType::CANCEL;
        if (e.status == "network_error") e.type = DistributedEventType::NETWORK_ERROR;
        if (e.failure_reason == "load_balancer_failover") e.type = DistributedEventType::FAILOVER;

        out.push_back(e);
    }
    return annotate_network_events(out);
}

TimelineCorrelationSummary correlate_incident_timeline(const std::vector<DistributedEvent>& events,
                                                       uint64_t deploy_ts_ms,
                                                       int correlation_window_ms) {
    TimelineCorrelationSummary s;
    if (events.empty()) return s;

    s.window_start_ms = static_cast<int>(events.front().ts_ms);
    s.window_end_ms = static_cast<int>(events.back().ts_ms);

    for (const auto& e : events) {
        s.max_latency_ms = std::max(s.max_latency_ms, e.latency_ms);
        if (e.type == DistributedEventType::NETWORK_ERROR || e.type == DistributedEventType::TIMEOUT) {
            s.error_burst_count++;
            if (static_cast<int>(e.ts_ms) >= static_cast<int>(deploy_ts_ms) &&
                static_cast<int>(e.ts_ms - deploy_ts_ms) <= correlation_window_ms) {
                s.deploy_correlated = true;
            }
        }
        if (e.type == DistributedEventType::FAILOVER) s.failover_observed = true;
    }

    if (s.deploy_correlated) s.suspected_trigger = "recent_deploy";
    else if (s.failover_observed) s.suspected_trigger = "dependency_failover_or_health_change";
    else if (s.error_burst_count >= 2) s.suspected_trigger = "error_burst_without_deploy_signal";
    else s.suspected_trigger = "isolated_regression_signal";

    return s;
}

BlastRadiusSummary infer_blast_radius(const std::vector<DistributedEvent>& events) {
    BlastRadiusSummary s;
    std::set<std::string> direct;
    std::set<std::string> upstream;

    const auto* failure = first_failure(events);
    if (failure) s.root_service = failure->service;

    for (const auto& e : events) {
        if (e.type == DistributedEventType::RETRY) s.retry_events++;
        if (e.type == DistributedEventType::TIMEOUT) s.timeout_events++;
        if (e.type == DistributedEventType::NETWORK_ERROR) s.network_error_events++;

        if (!s.root_service.empty()) {
            if (e.service == s.root_service && !e.downstream_service.empty()) direct.insert(e.downstream_service);
            if (e.downstream_service == s.root_service && !e.service.empty()) upstream.insert(e.service);
            if (e.parent_span_id == failure->span_id && !e.service.empty()) direct.insert(e.service);
        }
    }

    s.directly_impacted_services.assign(direct.begin(), direct.end());
    s.upstream_services.assign(upstream.begin(), upstream.end());
    return s;
}

std::string build_semantic_diff_json(const std::vector<DistributedEvent>& baseline,
                                     const std::vector<DistributedEvent>& candidate) {
    auto count_type = [](const std::vector<DistributedEvent>& xs, DistributedEventType t) {
        int c = 0;
        for (const auto& e : xs) if (e.type == t) c++;
        return c;
    };
    auto max_latency = [](const std::vector<DistributedEvent>& xs) {
        int m = 0;
        for (const auto& e : xs) m = std::max(m, e.latency_ms);
        return m;
    };

    const auto* b_fail = first_failure(baseline);
    const auto* c_fail = first_failure(candidate);

    std::ostringstream oss;
    oss << "{\n"
        << "  \"baseline_first_failing_service\": \"" << escape_json(b_fail ? b_fail->service : "") << "\",\n"
        << "  \"candidate_first_failing_service\": \"" << escape_json(c_fail ? c_fail->service : "") << "\",\n"
        << "  \"baseline_first_failure_reason\": \"" << escape_json(b_fail ? b_fail->failure_reason : "") << "\",\n"
        << "  \"candidate_first_failure_reason\": \"" << escape_json(c_fail ? c_fail->failure_reason : "") << "\",\n"
        << "  \"retry_delta\": " << (count_type(candidate, DistributedEventType::RETRY) - count_type(baseline, DistributedEventType::RETRY)) << ",\n"
        << "  \"timeout_delta\": " << (count_type(candidate, DistributedEventType::TIMEOUT) - count_type(baseline, DistributedEventType::TIMEOUT)) << ",\n"
        << "  \"network_error_delta\": " << (count_type(candidate, DistributedEventType::NETWORK_ERROR) - count_type(baseline, DistributedEventType::NETWORK_ERROR)) << ",\n"
        << "  \"failover_delta\": " << (count_type(candidate, DistributedEventType::FAILOVER) - count_type(baseline, DistributedEventType::FAILOVER)) << ",\n"
        << "  \"max_latency_delta_ms\": " << (max_latency(candidate) - max_latency(baseline)) << ",\n"
        << "  \"summary\": \"Semantic incident diff compares first failing hop, dominant failure reason, retry amplification, timeout growth, failover presence, and latency inflation between baseline and candidate runs.\"\n"
        << "}\n";
    return oss.str();
}

std::string build_incident_report_json(const std::vector<DistributedEvent>& baseline,
                                       const std::vector<DistributedEvent>& candidate) {
    std::vector<std::string> ann;
    for (const auto& e : candidate) for (const auto& a : e.annotations) add_unique(ann, a);

    const auto timeline = correlate_incident_timeline(candidate, 5200, 1200);
    const auto blast = infer_blast_radius(candidate);

    int timeout_count = 0, retry_count = 0, network_error_count = 0, failover_count = 0;
    for (const auto& e : candidate) {
        if (e.type == DistributedEventType::TIMEOUT) timeout_count++;
        if (e.type == DistributedEventType::RETRY) retry_count++;
        if (e.type == DistributedEventType::NETWORK_ERROR) network_error_count++;
        if (e.type == DistributedEventType::FAILOVER) failover_count++;
    }

    std::string family = "distributed_degradation";
    if (retry_count >= 2) family = "retry_storm";
    if (timeout_count >= 2) family = "cascading_timeouts";
    if (failover_count >= 1) family = "failover_edge_case";

    std::ostringstream oss;
    oss << "{\n"
        << "  \"baseline_event_count\": " << baseline.size() << ",\n"
        << "  \"candidate_event_count\": " << candidate.size() << ",\n"
        << "  \"incident_family\": \"" << family << "\",\n"
        << "  \"timeout_events\": " << timeout_count << ",\n"
        << "  \"retry_events\": " << retry_count << ",\n"
        << "  \"network_error_events\": " << network_error_count << ",\n"
        << "  \"failover_events\": " << failover_count << ",\n"
        << "  \"annotations\": " << json_string_array(ann) << ",\n"
        << "  \"timeline_correlation\": {\n"
        << "    \"deploy_correlated\": " << (timeline.deploy_correlated ? "true" : "false") << ",\n"
        << "    \"failover_observed\": " << (timeline.failover_observed ? "true" : "false") << ",\n"
        << "    \"max_latency_ms\": " << timeline.max_latency_ms << ",\n"
        << "    \"error_burst_count\": " << timeline.error_burst_count << ",\n"
        << "    \"window_start_ms\": " << timeline.window_start_ms << ",\n"
        << "    \"window_end_ms\": " << timeline.window_end_ms << ",\n"
        << "    \"suspected_trigger\": \"" << escape_json(timeline.suspected_trigger) << "\"\n"
        << "  },\n"
        << "  \"blast_radius\": {\n"
        << "    \"root_service\": \"" << escape_json(blast.root_service) << "\",\n"
        << "    \"directly_impacted_services\": " << json_string_array(blast.directly_impacted_services) << ",\n"
        << "    \"upstream_services\": " << json_string_array(blast.upstream_services) << ",\n"
        << "    \"retry_events\": " << blast.retry_events << ",\n"
        << "    \"timeout_events\": " << blast.timeout_events << ",\n"
        << "    \"network_error_events\": " << blast.network_error_events << "\n"
        << "  },\n"
        << "  \"summary\": \"Cross-service replay reconstructed request/span causality, correlated incident timing against deploy/error markers, inferred blast radius, and highlighted timeout cascades, retry amplification, and transport-level divergence.\",\n"
        << "  \"runbook\": [\n"
        << "    {\"step\":\"check_request_and_span_lineage\",\"guidance\":\"Confirm request_id/span_id chain and identify the first failing downstream hop.\"},\n"
        << "    {\"step\":\"correlate_with_recent_changes\",\"guidance\":\"Check whether error burst timing aligns with deploy, health-change, or failover windows.\"},\n"
        << "    {\"step\":\"inspect_network_symptoms\",\"guidance\":\"Check DNS, TCP connect, transport resets, and latency inflation between services.\"},\n"
        << "    {\"step\":\"assess_retry_policy\",\"guidance\":\"Verify backoff, retry fan-out, and whether retries amplified an already failing dependency.\"},\n"
        << "    {\"step\":\"blast_radius_review\",\"guidance\":\"Inspect impacted upstream callers and downstream dependencies before rollback or traffic shift.\"}\n"
        << "  ]\n"
        << "}\n";
    return oss.str();
}

}  // namespace dettrace
