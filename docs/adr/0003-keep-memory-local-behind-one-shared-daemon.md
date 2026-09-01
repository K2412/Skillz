# Keep memory local behind one shared daemon

Supersede ADRs 0001 and 0002: encrypted local SQLite is the sole canonical and retrieval store, and one loopback-only `launchd` daemon owns SQLite, FastEmbed, and the encrypted outbox for every supported client. Turso and Qdrant are not part of the active or planned authority path; any future redundancy requires a separate decision and may only copy a verified encrypted snapshot one way.
