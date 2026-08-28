# Reliable account-neutral recovery for Responses bridge

Separate the optimized `previous_response_id` delta request from the original
complete client transcript. When an upstream account rejects a quota-bound
request or an injected previous-response anchor before visible output, the
bridge MUST replay the complete portable transcript and walk eligible
accounts. Normal routing policy, sticky ownership, and non-quota recovery
remain unchanged.

