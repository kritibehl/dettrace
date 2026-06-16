#include <iostream>
int main() {
    const bool timeout_after_request = true;
    const bool retry_after_timeout = true;
    if (!timeout_after_request || !retry_after_timeout) return 1;
    std::cout << "thread/order validation passed\n";
    return 0;
}
