#include "dettrace/invariants.hpp"
#include <stdexcept>
#include <unordered_map>
#include <string>

namespace dettrace {

enum class TaskState {
    NONE,
    ENQUEUED,
    DEQUEUED,
    STARTED,
    FINISHED
};

static std::string state_str(TaskState s) {
    switch (s) {
        case TaskState::NONE:     return "NONE";
        case TaskState::ENQUEUED: return "ENQUEUED";
        case TaskState::DEQUEUED: return "DEQUEUED";
        case TaskState::STARTED:  return "STARTED";
        case TaskState::FINISHED: return "FINISHED";
    }
    return "UNKNOWN";
}

static void fail(uint64_t seq, int task, const std::string& msg) {
    throw std::runtime_error(
        "Invariant failed at seq=" + std::to_string(seq) +
        " task=" + std::to_string(task) +
        " : " + msg
    );
}

void verify_invariants_or_throw(const std::vector<Event>& events) {
    std::unordered_map<int, TaskState> state;

    // Strong invariant: seq numbers are contiguous
    for (size_t i = 0; i < events.size(); i++) {
        if (events[i].seq != static_cast<uint64_t>(i)) {
            fail(events[i].seq, events[i].task,
                 "non-contiguous seq (expected " + std::to_string(i) + ")");
        }
    }

    for (const auto& e : events) {
        TaskState cur = state.count(e.task) ? state[e.task] : TaskState::NONE;

        switch (e.type) {
            case EventType::TASK_ENQUEUED:
                if (cur != TaskState::NONE) {
                    fail(e.seq, e.task, "ENQUEUED but state is " + state_str(cur));
                }
                state[e.task] = TaskState::ENQUEUED;
                break;

            case EventType::TASK_DEQUEUED:
                if (cur != TaskState::ENQUEUED) {
                    fail(e.seq, e.task, "DEQUEUED but state is " + state_str(cur));
                }
                state[e.task] = TaskState::DEQUEUED;
                break;

            case EventType::TASK_STARTED:
                if (cur != TaskState::DEQUEUED) {
                    fail(e.seq, e.task, "STARTED but state is " + state_str(cur));
                }
                state[e.task] = TaskState::STARTED;
                break;

            case EventType::TASK_FINISHED:
                if (cur != TaskState::STARTED) {
                    fail(e.seq, e.task, "FINISHED but state is " + state_str(cur));
                }
                state[e.task] = TaskState::FINISHED;
                break;
        }
    }

    // Final invariant: every task must finish
    for (const auto& [task, st] : state) {
        if (st != TaskState::FINISHED) {
            fail(events.back().seq, task,
                 "task did not reach FINISHED (ended at " + state_str(st) + ")");
        }
    }
}

} // namespace dettrace
