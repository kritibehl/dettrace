#include "dettrace/trace_io.hpp"
#include "dettrace/event.hpp"

#include <cassert>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <vector>

namespace fs = std::filesystem;

static int first_divergence_index(const std::vector<dettrace::Event>& a,
                                  const std::vector<dettrace::Event>& b) {
    const size_t n = std::min(a.size(), b.size());
    for (size_t i = 0; i < n; ++i) {
        if (a[i].seq != b[i].seq ||
            a[i].type != b[i].type ||
            a[i].task != b[i].task ||
            a[i].worker != b[i].worker ||
            a[i].queue != b[i].queue) {
            return static_cast<int>(i);
        }
    }
    if (a.size() != b.size()) return static_cast<int>(n);
    return -1;
}

int main() {
    const int rc = std::system("./build/dettrace > /tmp/dettrace_test_output.txt 2>&1");
    assert(rc == 0);

    assert(fs::exists("artifacts/expected.jsonl"));
    assert(fs::exists("artifacts/actual.jsonl"));

    const auto expected = dettrace::read_trace_jsonl("artifacts/expected.jsonl");
    const auto actual   = dettrace::read_trace_jsonl("artifacts/actual.jsonl");

    assert(!expected.empty());
    assert(!actual.empty());

    const int idx = first_divergence_index(expected, actual);
    assert(idx == 5);

    const auto& e = expected.at(static_cast<size_t>(idx));
    const auto& a = actual.at(static_cast<size_t>(idx));

    assert(e.type == dettrace::EventType::TASK_DEQUEUED);
    assert(a.type == dettrace::EventType::TASK_DEQUEUED);

    assert(e.task.has_value());
    assert(a.task.has_value());
    assert(e.task.value() == 1);
    assert(a.task.value() == 2);

    std::cout << "PASS: flaky_case_1 divergence detected at index 5\n";
    return 0;
}
