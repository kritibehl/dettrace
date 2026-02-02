#include "dettrace/diff.hpp"
#include <sstream>

namespace dettrace {

static std::string event_to_string(const Event& e) {
    std::ostringstream oss;
    oss << "{seq=" << e.seq
        << ", type=" << to_string(e.type)
        << ", task=" << e.task
        << ", worker=" << (e.worker ? std::to_string(*e.worker) : "null")
        << ", queue="  << (e.queue  ? std::to_string(*e.queue)  : "null")
        << "}";
    return oss.str();
}

static bool same_opt(const std::optional<int>& a, const std::optional<int>& b) {
    if (!a.has_value() && !b.has_value()) return true;
    if (a.has_value() != b.has_value()) return false;
    return *a == *b;
}

static bool events_equal_ignoring_seq(const Event& a, const Event& b) {
    return a.type == b.type &&
           a.task == b.task &&
           same_opt(a.worker, b.worker) &&
           same_opt(a.queue, b.queue);
}

DiffResult diff_traces(const std::vector<Event>& expected,
                       const std::vector<Event>& actual) {
    DiffResult r;

    size_t n = std::min(expected.size(), actual.size());
    for (size_t i = 0; i < n; i++) {
        // We ignore seq because seq will always match index,
        // and mismatch should be about semantic divergence.
        if (!events_equal_ignoring_seq(expected[i], actual[i])) {
            r.identical = false;
            r.index = i;

            std::ostringstream oss;
            oss << "First mismatch at index=" << i << "\n"
                << "EXPECTED: " << event_to_string(expected[i]) << "\n"
                << "ACTUAL:   " << event_to_string(actual[i]);
            r.message = oss.str();
            return r;
        }
    }

    if (expected.size() != actual.size()) {
        r.identical = false;
        r.index = n;

        std::ostringstream oss;
        oss << "Trace length mismatch at index=" << n
            << " expected_size=" << expected.size()
            << " actual_size="   << actual.size();
        r.message = oss.str();
        return r;
    }

    r.identical = true;
    r.message = "Traces are identical";
    return r;
}

} // namespace dettrace
