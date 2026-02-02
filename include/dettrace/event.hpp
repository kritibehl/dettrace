#pragma once
#include <string>
#include <optional>
#include <cstdint>

namespace dettrace {

// What kind of event happened?
enum class EventType {
    TASK_ENQUEUED,
    TASK_DEQUEUED,
    TASK_STARTED,
    TASK_FINISHED
};

// Convert enum -> string (for printing / trace files)
std::string to_string(EventType t);

// Convert string -> enum (for reading trace files later)
EventType event_type_from_string(const std::string& s);

// One recorded event in the trace
struct Event {
    uint64_t seq = 0;          // strictly increasing event id (0,1,2,...)
    EventType type;            // event type

    int task = -1;             // which task the event refers to
    std::optional<int> worker; // which worker (if relevant)
    std::optional<int> queue;  // which queue (if relevant)
};

} // namespace dettrace
