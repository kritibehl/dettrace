#include "dettrace/replay_guard.hpp"
#include <sstream>
#include <stdexcept>

namespace dettrace {

ReplayGuard::ReplayGuard(const std::vector<Event>& expected)
    : expected_(expected) {}

bool ReplayGuard::same_opt(const std::optional<int>& a, const std::optional<int>& b) {
    if (!a.has_value() && !b.has_value()) return true;
    if (a.has_value() != b.has_value()) return false;
    return *a == *b;
}

std::string ReplayGuard::event_to_string(const Event& e) {
    std::ostringstream oss;
    oss << "{type=" << to_string(e.type)
        << ", task=" << e.task
        << ", worker=" << (e.worker ? std::to_string(*e.worker) : "null")
        << ", queue="  << (e.queue  ? std::to_string(*e.queue)  : "null")
        << "}";
    return oss.str();
}

void ReplayGuard::on_event(EventType type,
                           int task,
                           std::optional<int> worker,
                           std::optional<int> queue) {
    if (idx_ >= expected_.size()) {
        throw std::runtime_error("ReplayGuard: extra event emitted at index=" + std::to_string(idx_));
    }

    const Event& exp = expected_[idx_];

    // Compare semantic fields (ignore exp.seq)
    bool ok =
        exp.type == type &&
        exp.task == task &&
        same_opt(exp.worker, worker) &&
        same_opt(exp.queue, queue);

    if (!ok) {
        Event got;
        got.seq = 0; // irrelevant
        got.type = type;
        got.task = task;
        got.worker = worker;
        got.queue = queue;

        std::ostringstream oss;
        oss << "ReplayGuard mismatch at index=" << idx_ << "\n"
            << "EXPECTED: " << event_to_string(exp) << "\n"
            << "GOT:      " << event_to_string(got);

        throw std::runtime_error(oss.str());
    }

    idx_++;
}

void ReplayGuard::finish() {
    if (idx_ != expected_.size()) {
        throw std::runtime_error(
            "ReplayGuard: trace not fully consumed. consumed=" +
            std::to_string(idx_) + " expected=" + std::to_string(expected_.size())
        );
    }
}

} // namespace dettrace
