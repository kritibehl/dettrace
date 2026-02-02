#pragma once

#include "dettrace/event.hpp"
#include "dettrace/recorder.hpp"
#include <vector>

namespace dettrace {

// Trace-driven replayer.
// It "executes" a run by consuming the expected event sequence.
// It can either:
//  (A) just validate that expected trace is internally consistent (already done by invariants), OR
//  (B) validate that a new run produces exactly the same events (next step: hook into scheduler)
//
// For MVP, we implement A + a simple trace-driven simulation that reproduces the same events.
class Replayer {
public:
    explicit Replayer(const std::vector<Event>& expected);

    // Reconstruct an equivalent execution by iterating expected events
    // and re-emitting them into a Recorder.
    Recorder replay_to_recorder() const;

private:
    const std::vector<Event>& expected_;
};

} // namespace dettrace
