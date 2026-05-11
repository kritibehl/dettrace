CXX ?= c++
CC ?= cc

CXXFLAGS ?= -std=c++17 -Wall -Wextra -O2
CFLAGS ?= -std=c11 -Wall -Wextra -O2

CPP_TARGET := replay_device_trace
C_TARGET := replay_c_api_demo

.PHONY: all cpp c run clean

all: cpp c

cpp:
	$(CXX) $(CXXFLAGS) replay_device_trace.cpp -o $(CPP_TARGET)

c:
	$(CC) $(CFLAGS) replay_result.c replay_c_api_demo.c -o $(C_TARGET)

run: all
	./$(CPP_TARGET) || true
	./$(C_TARGET)

clean:
	rm -f $(CPP_TARGET) $(C_TARGET)
	rm -rf reports
