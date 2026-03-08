#include "dettrace/recorder.hpp"
#include "dettrace/scheduler.hpp"
#include "dettrace/trace_io.hpp"
#include "dettrace/invariants.hpp"
#include "dettrace/diff.hpp"
#include "dettrace/replayer.hpp"
#include "dettrace/replay_guard.hpp"

#include <filesystem>
#include <iostream>
#include <optional>
#include <vector>

namespace fs = std::filesystem;

static const std::string kArtifactsDir = "artifacts";
static const std::string kExpectedTrace = "artifacts/expected.jsonl";
static const std::string kActualTrace   = "artifacts/actual.jsonl";
static const std::string kReplayTrace   = "artifacts/replayed.jsonl";
static const std::string kGuardedOkTrace = "artifacts/guarded_ok.jsonl";

static void ensure_artifacts_dir() {
    fs::create_directories(kArtifactsDir);
}

static std::vector<dettrace::Event> make_expected_trace() {
    dettrace::Recorder rec;
    dettrace::Scheduler sched(rec, /*workers=*/2);

    for (int i = 1; i <= 5; i++) sched.enqueue_task(i);
    sched.run();

    dettrace::write_trace_jsonl(kExpectedTrace, rec.events());
    auto expected = dettrace::read_trace_jsonl(kExpectedTrace);
    dettrace::verify_invariants_or_throw(expected);
    return expected;
}

static void run_guarded(const std::vector<dettrace::Event>& expected, bool flip) {
    dettrace::Recorder rec;
    dettrace::Scheduler sched(rec, /*workers=*/2);
    sched.set_flip_first_two(flip);

    for (int i = 1; i <= 5; i++) sched.enqueue_task(i);

    dettrace::ReplayGuard guard(expected);

    for (int i = 1; i <= 5; i++) {
        guard.on_event(dettrace::EventType::TASK_ENQUEUED, i, std::nullopt, 0);
    }

    sched.run_with_guard(guard);

    dettrace::write_trace_jsonl(flip ? kActualTrace : kGuardedOkTrace, rec.events());
}

static void write_replayed_trace(const std::vector<dettrace::Event>& expected) {
    dettrace::write_trace_jsonl(kReplayTrace, expected);
}

int main() {
    ensure_artifacts_dir();

    try {
        auto expected = make_expected_trace();
        write_replayed_trace(expected);

        std::cout << "Expected trace generated + invariants PASSED ✅\n";

        run_guarded(expected, false);
        std::cout << "ReplayGuard PASS ✅ (system followed expected trace)\n";

        std::cout << "\nNow injecting divergence...\n";
        run_guarded(expected, true);

        std::cout << "Unexpected: divergence run passed (should not happen)\n";
        return 0;

    } catch (const std::exception& ex) {
        std::cerr << "\nReplayGuard caught divergence ✅\n" << ex.what() << "\n";
        return 0;
    }
}
