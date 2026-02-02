#pragma once

#include "dettrace/event.hpp"
#include <vector>
#include <optional>
#include <cstdint>

namespace dettrace {

class Recorder {
public:
    void record(EventType type,
                int task,
                std::optional<int> worker = std::nullopt,
                std::optional<int> queue  = std::nullopt);

    const std::vector<Event>& events() const { return events_; }

private:
    uint64_t next_seq_ = 0;
    std::vector<Event> events_;
};

} // namespace dettrace
