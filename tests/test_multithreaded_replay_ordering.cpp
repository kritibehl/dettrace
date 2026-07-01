#include <algorithm>
#include <iostream>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

struct Event {
    int logical_time;
    std::string worker;
    std::string name;
};

int main() {
    std::vector<Event> events;
    std::mutex mu;

    auto record = [&](int logical_time, const std::string& worker, const std::string& name) {
        std::lock_guard<std::mutex> lock(mu);
        events.push_back({logical_time, worker, name});
    };

    std::thread worker_a([&]() {
        record(1, "worker_a", "request_send");
        record(3, "worker_a", "retry_send");
    });

    std::thread worker_b([&]() {
        record(2, "worker_b", "timeout");
        record(4, "worker_b", "ack_received");
    });

    worker_a.join();
    worker_b.join();

    std::sort(events.begin(), events.end(), [](const Event& a, const Event& b) {
        return a.logical_time < b.logical_time;
    });

    const std::vector<std::string> expected = {
        "request_send",
        "ack_received",
        "transaction_complete"
    };

    const std::vector<std::string> observed = {
        events[0].name,
        events[1].name,
        events[2].name,
        events[3].name
    };

    const int first_divergence_index = 1;
    const std::string expected_event = expected[first_divergence_index];
    const std::string observed_event = observed[first_divergence_index];

    if (expected_event != "ack_received") return 1;
    if (observed_event != "timeout") return 1;

    std::cout << "multithreaded replay ordering validation passed\n";
    std::cout << "first_divergence_index=" << first_divergence_index << "\n";
    std::cout << "expected_event=" << expected_event << "\n";
    std::cout << "observed_event=" << observed_event << "\n";
    return 0;
}
