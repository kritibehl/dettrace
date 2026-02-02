#include "dettrace/replayer.hpp"

namespace dettrace {

Replayer::Replayer(const std::vector<Event>& expected)
    : expected_(expected) {}

Recorder Replayer::replay_to_recorder() const {
    Recorder rec;
    for (const auto& e : expected_) {
        rec.record(e.type, e.task, e.worker, e.queue);
    }
    return rec;
}

} // namespace dettrace
