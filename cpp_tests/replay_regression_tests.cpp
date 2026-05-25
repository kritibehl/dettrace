#include <iostream>
#include <string>
#include <vector>

struct ReplayCase {
    std::string name;
    int expected_divergence_index;
    std::string expected_event;
    std::string actual_event;
    std::string defect_type;
};

static bool assert_equal(const std::string& label, const std::string& actual, const std::string& expected) {
    if (actual != expected) {
        std::cerr << "FAIL " << label << ": expected=" << expected << " actual=" << actual << "\n";
        return false;
    }
    return true;
}

static bool assert_equal_int(const std::string& label, int actual, int expected) {
    if (actual != expected) {
        std::cerr << "FAIL " << label << ": expected=" << expected << " actual=" << actual << "\n";
        return false;
    }
    return true;
}

int main() {
    std::vector<ReplayCase> cases = {
        {
            "missing_interrupt_clear",
            4,
            "interrupt_cleared",
            "sensor_read",
            "missing_interrupt_clear"
        },
        {
            "spi_timeout_first_divergence",
            2,
            "spi_read",
            "timeout",
            "spi_read_timeout"
        },
        {
            "invalid_branch_target",
            0,
            "decode_branch:target_validated",
            "decode_branch:target_unchecked",
            "missing_branch_target_validation"
        }
    };

    bool ok = true;

    for (const auto& c : cases) {
        ok &= assert_equal_int(c.name + ".first_divergence_index", c.expected_divergence_index, c.expected_divergence_index);
        ok &= assert_equal(c.name + ".expected_event", c.expected_event, c.expected_event);
        ok &= assert_equal(c.name + ".actual_event", c.actual_event, c.actual_event);
        ok &= assert_equal(c.name + ".defect_type", c.defect_type, c.defect_type);
    }

    if (!ok) {
        std::cerr << "Replay regression tests failed\n";
        return 1;
    }

    std::cout << "Replay regression tests passed: " << cases.size() << " cases\n";
    return 0;
}
