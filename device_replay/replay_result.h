#ifndef DETTRACE_REPLAY_RESULT_H
#define DETTRACE_REPLAY_RESULT_H

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ReplayResult {
    int first_divergence_index;
    const char* expected_event;
    const char* actual_event;
    const char* expected_state;
    const char* actual_state;
    const char* probable_defect_type;
} ReplayResult;

ReplayResult dettrace_sample_device_replay_result(void);
void dettrace_print_replay_result(const ReplayResult* result);

#ifdef __cplusplus
}
#endif

#endif
