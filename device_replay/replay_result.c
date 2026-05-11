#include "replay_result.h"

#include <stdio.h>

ReplayResult dettrace_sample_device_replay_result(void) {
    ReplayResult result;
    result.first_divergence_index = 4;
    result.expected_event = "interrupt_cleared";
    result.actual_event = "sensor_read";
    result.expected_state = "READY";
    result.actual_state = "WAITING";
    result.probable_defect_type = "missing_interrupt_clear";
    return result;
}

void dettrace_print_replay_result(const ReplayResult* result) {
    if (result == NULL) {
        return;
    }

    printf("ReplayResult\\n");
    printf("============\\n");
    printf("first_divergence_index: %d\\n", result->first_divergence_index);
    printf("expected_event: %s\\n", result->expected_event);
    printf("actual_event: %s\\n", result->actual_event);
    printf("expected_state: %s\\n", result->expected_state);
    printf("actual_state: %s\\n", result->actual_state);
    printf("probable_defect_type: %s\\n", result->probable_defect_type);
}
