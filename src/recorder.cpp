#include "dettrace/recorder.hpp"

namespace dettrace {

void Recorder::record(EventType type,
                      int task,
                      std::optional<int> worker,
                      std::optional<int> queue) {
    Event e;
    e.seq = next_seq_++;
    e.type = type;
    e.task = task;
    e.worker = worker;
    e.queue  = queue;
    events_.push_back(e);
}

} // namespace dettrace
