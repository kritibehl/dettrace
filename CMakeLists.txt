cmake_minimum_required(VERSION 3.16)
project(dettrace CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(include)

add_executable(dettrace
  src/main.cpp
  src/event.cpp
  src/recorder.cpp
  src/scheduler.cpp
  src/trace_io.cpp
  src/invariants.cpp
  src/diff.cpp
  src/replayer.cpp
  src/replay_guard.cpp
)

enable_testing()

add_executable(test_flaky_case_1
    tests/integration/test_flaky_case_1.cpp
    src/event.cpp
    src/trace_io.cpp
)

target_include_directories(test_flaky_case_1 PRIVATE include)

add_test(NAME flaky_case_1 COMMAND test_flaky_case_1)
