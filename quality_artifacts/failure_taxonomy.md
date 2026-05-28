# Failure Taxonomy

| Failure Family | Description |
|---|---|
| reconnect_recovery | temporary disconnect followed by valid recovery |
| enumeration_timeout | device enumeration cannot complete after config/read timeout |
| link_training_retry | link-training timeout recovers through retry |
| accessory_session_recovery | accessory disconnect/reconnect revalidates capability/session state |
| timeout_retry_chain | timeout path recovers through bounded retries |
