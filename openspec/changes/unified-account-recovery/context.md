# Context

The previous implementation mixed continuity ownership and pool failover. A quota response could leave the failed owner as the preferred account while a prompt-cache affinity key was still supplied to the balancer. The balancer then revisited the same owner or returned its quota error without selecting a replacement. Recovery now has an explicit detached-fallback boundary: account-owned affinity is retained for normal routing, but is removed for the current retry after that owner is excluded. The original request body remains authoritative for replay.
