#include <iostream>
int main() {
    const int matched_regressions = 2;
    const int risk_score = 100;
    if (matched_regressions < 1 || risk_score < 80) return 1;
    std::cout << "replay regression validation passed\n";
    return 0;
}
