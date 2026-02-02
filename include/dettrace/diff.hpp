#pragma once

#include "dettrace/event.hpp"
#include <vector>
#include <string>

namespace dettrace {

struct DiffResult {
    bool identical = true;
    size_t index = 0;            // first mismatch index
    std::string message;         // human friendly explanation
};

// Compare two traces and return first mismatch (or identical=true).
DiffResult diff_traces(const std::vector<Event>& expected,
                       const std::vector<Event>& actual);

} // namespace dettrace
