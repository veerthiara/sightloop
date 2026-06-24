#!/bin/sh

branch_name() {
    git symbolic-ref --quiet --short HEAD 2>/dev/null
}

is_phase_branch() {
    printf '%s\n' "$1" | grep -Eq '^phase-[0-9]{2}-rev-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*$'
}

validate_branch_name() {
    branch="$(branch_name)"

    if [ -z "$branch" ]; then
        return 0
    fi

    if [ "$branch" = "main" ]; then
        return 0
    fi

    if is_phase_branch "$branch"; then
        return 0
    fi

    cat >&2 <<EOF
Invalid branch name: $branch

Use:
  main
  phase-00-rev-02-foundation
  phase-01-rev-01-detection
  phase-02-rev-01-tracking-and-zones
EOF
    return 1
}

phase_commit_prefix_regex() {
    branch="$1"
    phase_padded="$(printf '%s\n' "$branch" | sed -E 's/^phase-([0-9]{2})-.*/\1/')"
    phase_plain="$(printf '%s\n' "$phase_padded" | sed -E 's/^0*([0-9]+)$/\1/')"
    rev="$(printf '%s\n' "$branch" | sed -E 's/^phase-[0-9]{2}-rev-([0-9]{2})-.*/\1/')"

    if [ -z "$phase_plain" ]; then
        phase_plain="0"
    fi

    printf '^phase-(%s|%s) rev-%s: .+' "$phase_padded" "$phase_plain" "$rev"
}
