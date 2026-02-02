#pragma once

#include "dettrace/event.hpp"
#include <vector>

namespace dettrace {

// Verifies invariants on a trace.
// Throws std::runtime_error with a helpful message on first violation.
void verify_invariants_or_throw(const std::vector<Event>& events);

} // namespace dettrace
