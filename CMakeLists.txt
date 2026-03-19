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
set_tests_properties(flaky_case_1 PROPERTIES WORKING_DIRECTORY ${CMAKE_BINARY_DIR})


add_executable(dettrace_distributed
    src/distributed_main.cpp
    src/distributed_trace.cpp
)
target_include_directories(dettrace_distributed PRIVATE include)

add_executable(test_distributed_trace
    tests/integration/test_distributed_trace.cpp
    src/distributed_trace.cpp
)
target_include_directories(test_distributed_trace PRIVATE include)
add_test(NAME distributed_trace COMMAND test_distributed_trace)
set_tests_properties(distributed_trace PROPERTIES WORKING_DIRECTORY ${CMAKE_BINARY_DIR})

