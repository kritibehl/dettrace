cmake_minimum_required(VERSION 3.16)
project(DetTraceReplayValidation LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_executable(replay_device_trace
  device_replay/replay_device_trace.cpp
)

add_executable(replay_c_api_demo
  device_replay/replay_result.c
  device_replay/replay_c_api_demo.c
)

add_executable(replay_regression_tests
  cpp_tests/replay_regression_tests.cpp
)

enable_testing()
add_test(NAME replay_regression_tests COMMAND replay_regression_tests)
