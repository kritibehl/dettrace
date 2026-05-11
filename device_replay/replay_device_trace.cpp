#include <fstream>
#include <iostream>
#include <regex>
#include <sstream>
#include <string>
#include <vector>

struct Event {
    int index{};
    std::string event_type;
    std::string state;
    std::string value;
    std::string notes;
};

static std::string read_file(const std::string& path) {
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error("could not open " + path);
    }
    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

static std::string extract_string(const std::string& block, const std::string& key) {
    std::regex re("\"" + key + "\"\\s*:\\s*\"([^\"]*)\"");
    std::smatch match;
    if (std::regex_search(block, match, re)) {
        return match[1];
    }
    return "";
}

static int extract_int(const std::string& block, const std::string& key) {
    std::regex re("\"" + key + "\"\\s*:\\s*([0-9]+)");
    std::smatch match;
    if (std::regex_search(block, match, re)) {
        return std::stoi(match[1]);
    }
    return -1;
}

static std::vector<std::string> extract_objects_from_array(const std::string& json, const std::string& array_name) {
    std::vector<std::string> objects;
    const std::string marker = "\"" + array_name + "\"";
    auto start = json.find(marker);
    if (start == std::string::npos) return objects;

    auto array_start = json.find('[', start);
    auto array_end = json.find("]", array_start);
    if (array_start == std::string::npos || array_end == std::string::npos) return objects;

    std::string array = json.substr(array_start + 1, array_end - array_start - 1);

    size_t pos = 0;
    while (true) {
        auto obj_start = array.find('{', pos);
        if (obj_start == std::string::npos) break;
        auto obj_end = array.find('}', obj_start);
        if (obj_end == std::string::npos) break;
        objects.push_back(array.substr(obj_start, obj_end - obj_start + 1));
        pos = obj_end + 1;
    }

    return objects;
}

static std::vector<Event> parse_events(const std::string& json, const std::string& array_name, const std::string& state_key) {
    std::vector<Event> events;
    for (const auto& block : extract_objects_from_array(json, array_name)) {
        Event e;
        e.index = extract_int(block, "index");
        e.event_type = extract_string(block, "event_type");
        e.state = extract_string(block, state_key);
        e.value = extract_string(block, "value");
        e.notes = extract_string(block, "notes");
        events.push_back(e);
    }
    return events;
}

static std::string classify_defect(const Event& expected, const Event& actual) {
    if (expected.event_type == "interrupt_cleared" && actual.event_type != "interrupt_cleared") {
        return "missing_interrupt_clear";
    }
    if (actual.state == "WAITING" || actual.state == "DEGRADED") {
        return "stale_device_state";
    }
    if (expected.event_type != actual.event_type) {
        return "wrong_event_ordering";
    }
    if (expected.state != actual.state) {
        return "state_transition_mismatch";
    }
    return "unknown";
}

int main(int argc, char** argv) {
    const std::string path = argc > 1 ? argv[1] : "device_replay/sample_device_trace.json";

    try {
        const std::string json = read_file(path);
        const auto expected = parse_events(json, "expected", "expected_state");
        const auto actual = parse_events(json, "actual", "actual_state");

        int first_divergence = -1;
        Event expected_event;
        Event actual_event;

        const size_t n = std::min(expected.size(), actual.size());
        for (size_t i = 0; i < n; ++i) {
            if (expected[i].event_type != actual[i].event_type || expected[i].state != actual[i].state) {
                first_divergence = static_cast<int>(i);
                expected_event = expected[i];
                actual_event = actual[i];
                break;
            }
        }

        if (first_divergence == -1 && expected.size() != actual.size()) {
            first_divergence = static_cast<int>(n);
        }

        std::cout << "Device Event Replay Report\n";
        std::cout << "==========================\n";
        std::cout << "trace_file: " << path << "\n";

        if (first_divergence == -1) {
            std::cout << "status: PASS\n";
            std::cout << "first_divergence_index: none\n";
            return 0;
        }

        const auto defect = classify_defect(expected_event, actual_event);

        std::cout << "status: FAIL\n";
        std::cout << "first_divergence_index: " << first_divergence << "\n";
        std::cout << "expected_event: " << expected_event.event_type << "\n";
        std::cout << "actual_event: " << actual_event.event_type << "\n";
        std::cout << "expected_state: " << expected_event.state << "\n";
        std::cout << "actual_state: " << actual_event.state << "\n";
        std::cout << "probable_defect_type: " << defect << "\n";
        std::cout << "reproduction_steps:\n";
        std::cout << "  1. Replay sample_device_trace.json\n";
        std::cout << "  2. Follow expected events through firmware_timer_tick and interrupt_asserted\n";
        std::cout << "  3. Observe actual event at divergence index " << first_divergence << "\n";
        std::cout << "  4. Verify interrupt_cleared is missing before network_packet_received\n";

        return 1;
    } catch (const std::exception& ex) {
        std::cerr << "error: " << ex.what() << "\n";
        return 2;
    }
}
