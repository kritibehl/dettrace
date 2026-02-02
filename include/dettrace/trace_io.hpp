#pragma once

#include "dettrace/event.hpp"
#include <string>
#include <vector>

namespace dettrace {

// Writes events as JSON Lines (one JSON object per line)
void write_trace_jsonl(const std::string& path, const std::vector<Event>& events);

// Reads events from JSON Lines
std::vector<Event> read_trace_jsonl(const std::string& path);

} // namespace dettrace
