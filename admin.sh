#!/bin/bash
set -e

ARIADNE_ADMIN="${ARIADNE_ADMIN:-http://127.0.0.1:5577}"
BASIC_AUTH="${BASIC_AUTH:-}"
ACCOUNT="${ACCOUNT:-}"

EXTRA_CURL_ARGS=()
if [ "$BASIC_AUTH" ]; then
  EXTRA_CURL_ARGS+=("--user" "$BASIC_AUTH")
fi

cmd_test() {
  local result_str exit_code=0
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -X PUT --data-binary @- \
      "$ARIADNE_ADMIN/api/test?account=${ACCOUNT}"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_fcreate() {
  local user_id="$1"
  local comment="$2"
  local source="$3"
  data="$(jq --arg comment "$comment" --arg source "$source" '{comment: $comment, source: $source}' <<< "{}")"
  local result_str exit_code=0
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X PUT --data-binary "$data" \
      "$ARIADNE_ADMIN/api/friend/create?account=${ACCOUNT}&user_id=${user_id}"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_finherit() {
  local user_id="$1"
  local memo="$2"
  local history="$3"
  data="$(jq --arg memo "$memo" --arg history "$history" '{memo: $memo, history: $history}' <<< "{}")"
  local result_str exit_code=0
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X PUT --data-binary "$data" \
      "$ARIADNE_ADMIN/api/friend/inherit?account=${ACCOUNT}&user_id=${user_id}"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_fsend() {
  local user_id="$1"
  local message="$2"
  local result_str exit_code=0
  data="$(jq --arg message "$message" '{message: $message}' <<< "{}")"
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X POST --data-binary "$data" \
      "$ARIADNE_ADMIN/api/friend/send?account=${ACCOUNT}&user_id=${user_id}"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_gcreate() {
  local group_id="$1"
  local result_str exit_code=0
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X PUT --data-binary "{}" \
      "$ARIADNE_ADMIN/api/group/create?account=${ACCOUNT}&group_id=${group_id}"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_ginherit() {
  local group_id="$1"
  local memo="$2"
  local history="$3"
  data="$(jq --arg memo "$memo" --arg history "$history" '{memo: $memo, history: $history}' <<< "{}")"
  local result_str exit_code=0
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X PUT --data-binary "$data" \
      "$ARIADNE_ADMIN/api/group/inherit?account=${ACCOUNT}&group_id=${group_id}"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_gsend() {
  local group_id="$1"
  local message="$2"
  local result_str exit_code=0
  data="$(jq --arg message "$message" '{message: $message}' <<< "{}")"
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X POST --data-binary "$data" \
      "$ARIADNE_ADMIN/api/group/send?account=${ACCOUNT}&group_id=${group_id}"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_gwelcome() {
  local group_id="$1"
  local prompt="$2"
  local result_str exit_code=0
  data="$(jq --arg prompt "$prompt" '{prompt: $prompt}' <<< "{}")"
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X PUT --data-binary "$data" \
      "$ARIADNE_ADMIN/api/group/welcome?account=${ACCOUNT}&group_id=${group_id}"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_sget1() {
  local result_str exit_code=0
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X GET \
      "$ARIADNE_ADMIN/api/sensitive?id=1"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_sget2() {
  local result_str exit_code=0
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X GET \
      "$ARIADNE_ADMIN/api/sensitive?id=2"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_sadd1() {
  local result_str exit_code=0
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X PUT --data-binary @- \
      "$ARIADNE_ADMIN/api/sensitive?id=1"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_sadd2() {
  local result_str exit_code=0
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X PUT --data-binary @- \
      "$ARIADNE_ADMIN/api/sensitive?id=2"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_sdel1() {
  local result_str exit_code=0
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X DELETE --data-binary @- \
      "$ARIADNE_ADMIN/api/sensitive?id=1"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_sdel2() {
  local result_str exit_code=0
  result_str="$(
    curl "${EXTRA_CURL_ARGS[@]}" --fail-with-body -s \
      -H "Content-Type: application/json" \
      -X DELETE --data-binary @- \
      "$ARIADNE_ADMIN/api/sensitive?id=2"
  )" || exit_code="$?"
  echo "$result_str"
  return "$exit_code"
}

cmd_help(){
  printf 'Usage: %s COMMAND

Commands:
  test < <stdin>

  fcreate <user_id> [<comment>] [<source>]
  finherit <user_id> <memo> <history>
  fsend <user_id> <message>

  gcreate <group_id>
  ginherit <group_id> <memo> <history>
  gsend <group_id> <message>
  gwelcome <group_id> <prompt>

  sget1
  sget2
  sadd1 < <stdin>
  sadd2 < <stdin>
  sdel1 < <stdin>
  sdel2 < <stdin>

  help
' "$0"
}

main(){
  local cmd="$1"
  shift 2>/dev/null || true
  [ "$cmd" == "" ] && cmd=help  # default command
  [ "$cmd" == "-h" ] || [ "$cmd" == "--help" ] && cmd=help
  if ! type "cmd_$cmd" >/dev/null 2>&1; then
    cmd_help
    return 1
  fi
  cmd_$cmd "$@"
}

main "$@"
