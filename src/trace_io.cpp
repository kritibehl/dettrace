#include "dettrace/trace_io.hpp"
#include <fstream>
#include <stdexcept>

namespace dettrace {

// --- helpers (tiny + enough for our controlled format) ---

static std::string opt_int_to_json(const std::optional<int>& v) {
    return v.has_value() ? std::to_string(*v) : "null";
}

static std::optional<int> parse_optional_int(const std::string& s) {
    if (s == "null") return std::nullopt;
    return std::stoi(s);
}

// Extract value for key from our known JSON object format.
// Example: {"seq":0,"type":"TASK_ENQUEUED","task":1,"worker":null,"queue":0}
static std::string get_json_value(const std::string& line, const std::string& key) {
    const std::string pattern = "\"" + key + "\":";
    auto pos = line.find(pattern);
    if (pos == std::string::npos) throw std::runtime_error("Missing key: " + key);

    pos += pattern.size();

    // String value
    if (pos < line.size() && line[pos] == '"') {
        pos++;
        auto end = line.find('"', pos);
        if (end == std::string::npos) throw std::runtime_error("Bad string value for key: " + key);
        return line.substr(pos, end - pos);
    }

    // Number or null
    auto end = line.find_first_of(",}", pos);
    if (end == std::string::npos) throw std::runtime_error("Bad value for key: " + key);
    return line.substr(pos, end - pos);
}

// --- public API ---

void write_trace_jsonl(const std::string& path, const std::vector<Event>& events) {
    std::ofstream out(path);
    if (!out) throw std::runtime_error("Failed to open for write: " + path);

    for (const auto& e : events) {
        out << "{"
            << "\"seq\":" << e.seq << ","
            << "\"type\":\"" << to_string(e.type) << "\","
            << "\"task\":" << e.task << ","
            << "\"worker\":" << opt_int_to_json(e.worker) << ","
            << "\"queue\":"  << opt_int_to_json(e.queue)
            << "}\n";
    }
}

std::vector<Event> read_trace_jsonl(const std::string& path) {
    std::ifstream in(path);
    if (!in) throw std::runtime_error("Failed to open for read: " + path);

    std::vector<Event> events;
    std::string line;

    while (std::getline(in, line)) {
        if (line.empty()) continue;

        Event e;
        e.seq = static_cast<uint64_t>(std::stoull(get_json_value(line, "seq")));
        e.type = event_type_from_string(get_json_value(line, "type"));
        e.task = std::stoi(get_json_value(line, "task"));
        e.worker = parse_optional_int(get_json_value(line, "worker"));
        e.queue  = parse_optional_int(get_json_value(line, "queue"));

        events.push_back(e);
    }

    return events;
}

} // namespace dettrace
