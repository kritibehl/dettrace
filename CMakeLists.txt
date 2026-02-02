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
