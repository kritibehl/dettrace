#include "dettrace/scheduler.hpp"
#include <optional>

namespace dettrace {

Scheduler::Scheduler(Recorder& rec, int workers)
    : rec_(rec), workers_(workers) {}

void Scheduler::set_flip_first_two(bool enabled) {
    flip_first_two_ = enabled;
}

void Scheduler::emit(EventType type, int task,
                     std::optional<int> worker,
                     std::optional<int> queue,
                     ReplayGuard* guard) {
    // Always record
    rec_.record(type, task, worker, queue);

    // If guard is enabled, validate the emitted event
    if (guard) {
        guard->on_event(type, task, worker, queue);
    }
}

void Scheduler::enqueue_task(int task_id) {
    q_.push(task_id);
    emit(EventType::TASK_ENQUEUED, task_id, std::nullopt, 0, nullptr);
}

void Scheduler::run() {
    // no guard
    ReplayGuard* guard = nullptr;

    int worker = 0;
    bool flipped = false;

    while (!q_.empty()) {
        int task;

        if (flip_first_two_ && !flipped && q_.size() >= 2) {
            int a = q_.front(); q_.pop();
            int b = q_.front(); q_.pop();

            task = b;
            q_.push(a);
            flipped = true;
        } else {
            task = q_.front();
            q_.pop();
        }

        emit(EventType::TASK_DEQUEUED, task, worker, 0, guard);
        emit(EventType::TASK_STARTED,  task, worker, std::nullopt, guard);
        emit(EventType::TASK_FINISHED, task, worker, std::nullopt, guard);

        worker = (worker + 1) % workers_;
    }
}

void Scheduler::run_with_guard(ReplayGuard& g) {
    ReplayGuard* guard = &g;

    int worker = 0;
    bool flipped = false;

    while (!q_.empty()) {
        int task;

        if (flip_first_two_ && !flipped && q_.size() >= 2) {
            int a = q_.front(); q_.pop();
            int b = q_.front(); q_.pop();

            task = b;
            q_.push(a);
            flipped = true;
        } else {
            task = q_.front();
            q_.pop();
        }

        emit(EventType::TASK_DEQUEUED, task, worker, 0, guard);
        emit(EventType::TASK_STARTED,  task, worker, std::nullopt, guard);
        emit(EventType::TASK_FINISHED, task, worker, std::nullopt, guard);

        worker = (worker + 1) % workers_;
    }

    // Ensure expected trace fully consumed
    guard->finish();
}

} // namespace dettrace
