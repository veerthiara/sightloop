PHASE ?=
REV ?=
SLUG ?=

.PHONY: setup-git-hooks new-branch

setup-git-hooks:
	git config core.hooksPath .githooks
	@echo "Configured git hooks path to .githooks"
	@echo "Hooks now enforce branch naming, phase commit subjects, and backend pre-commit checks."

new-branch:
	@test -n "$(PHASE)" || (echo "PHASE is required, for example PHASE=00" >&2; exit 1)
	@test -n "$(REV)" || (echo "REV is required, for example REV=03" >&2; exit 1)
	@test -n "$(SLUG)" || (echo "SLUG is required, for example SLUG=camera-pipeline" >&2; exit 1)
	@printf '%s\n' "$(PHASE)" | grep -Eq '^[0-9]{2}$$' || (echo "PHASE must be two digits." >&2; exit 1)
	@printf '%s\n' "$(REV)" | grep -Eq '^[0-9]{2}$$' || (echo "REV must be two digits." >&2; exit 1)
	@printf '%s\n' "$(SLUG)" | grep -Eq '^[a-z0-9]+(-[a-z0-9]+)*$$' || (echo "SLUG must be lowercase kebab-case." >&2; exit 1)
	@branch="phase-$(PHASE)-rev-$(REV)-$(SLUG)"; \
	if git show-ref --verify --quiet "refs/heads/$$branch"; then \
		echo "Local branch already exists: $$branch" >&2; \
		exit 1; \
	fi; \
	if git show-ref --verify --quiet "refs/remotes/origin/$$branch"; then \
		echo "Remote branch already exists: origin/$$branch" >&2; \
		exit 1; \
	fi; \
	git checkout -b "$$branch"; \
	echo "Created and checked out $$branch"
