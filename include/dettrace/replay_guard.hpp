#pragma once

#include "dettrace/event.hpp"
#include <vector>
#include <string>
#include <optional>

namespace dettrace {

// ReplayGuard validates a live event stream against an expected trace.
// Call on_event(...) whenever the system emits an event.
// If mismatch, it throws with the first divergence.
class ReplayGuard {
public:
    explicit ReplayGuard(const std::vector<Event>& expected);

    // Validate one event (seq ignored; guard uses its own index)
    void on_event(EventType type,
                  int task,
                  std::optional<int> worker,
                  std::optional<int> queue);

    // Call at end to ensure expected trace was fully consumed.
    void finish();

private:
    const std::vector<Event>& expected_;
    size_t idx_ = 0;

    static std::string event_to_string(const Event& e);
    static bool same_opt(const std::optional<int>& a, const std::optional<int>& b);
};

} // namespace dettrace
