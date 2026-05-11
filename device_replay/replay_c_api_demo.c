#include "replay_result.h"

int main(void) {
    ReplayResult result = dettrace_sample_device_replay_result();
    dettrace_print_replay_result(&result);
    return result.first_divergence_index == 4 ? 0 : 1;
}
