#pragma once

#include "dettrace/recorder.hpp"
#include "dettrace/replay_guard.hpp"
#include <queue>

namespace dettrace {

class Scheduler {
public:
    Scheduler(Recorder& rec, int workers);

    void enqueue_task(int task_id);
    void set_flip_first_two(bool enabled);

    // Normal run (records events)
    void run();

    // Replay-validated run: emits events AND validates against expected trace
    void run_with_guard(ReplayGuard& guard);

private:
    Recorder& rec_;
    int workers_;
    std::queue<int> q_;
    bool flip_first_two_ = false;

    // helper to emit to recorder (+ optionally guard)
    void emit(EventType type, int task,
              std::optional<int> worker,
              std::optional<int> queue,
              ReplayGuard* guard);
};

} // namespace dettrace
