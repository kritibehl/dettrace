#include "dettrace/event.hpp"
#include <stdexcept>

namespace dettrace {

std::string to_string(EventType t) {
    switch (t) {
        case EventType::TASK_ENQUEUED: return "TASK_ENQUEUED";
        case EventType::TASK_DEQUEUED: return "TASK_DEQUEUED";
        case EventType::TASK_STARTED:  return "TASK_STARTED";
        case EventType::TASK_FINISHED: return "TASK_FINISHED";
    }
    return "UNKNOWN";
}

EventType event_type_from_string(const std::string& s) {
    if (s == "TASK_ENQUEUED") return EventType::TASK_ENQUEUED;
    if (s == "TASK_DEQUEUED") return EventType::TASK_DEQUEUED;
    if (s == "TASK_STARTED")  return EventType::TASK_STARTED;
    if (s == "TASK_FINISHED") return EventType::TASK_FINISHED;
    throw std::runtime_error("Unknown EventType: " + s);
}

} // namespace dettrace
