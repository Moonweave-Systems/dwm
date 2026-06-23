# Two-writer migration-team prompt

Use only after proving two independent workstreams.

1. Mapper freezes shared interface/schema and assigns integration owner.
2. Writer A and Writer B receive disjoint paths, base snapshot, forbidden paths,
   and separate worktrees.
3. Writers stop rather than altering shared contracts.
4. Integration owner merges and resolves semantic conflicts.
5. Test verifier runs integration checks on the merged snapshot.
6. Fresh reviewer examines the integrated diff, not individual claims.
7. Any unstable interface or shared-file conflict downgrades to sequential
   feature-pipeline.
8. Deterministic capture seals only the integrated attempt.
