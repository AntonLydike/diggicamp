#!/usr/bin/env bash

ls -lha ./
ls -lha /
ls -lha /diggicamp

FILE=/config/dgc.json
if ! test -f "$FILE"; then
  echo Initializing dgc...
  dgc init "$URL" --user "$USER" --pass "$PASS";
fi

RESULT=$(dgc show)
RAW_SEMESTER=$(echo "$RESULT" | grep -E "[WS]S.*:")
SEMESTER=${RAW_SEMESTER/":"/""}
SEMESTER=${SEMESTER/"/"/"_"}
SEMESTER=$(echo "$SEMESTER" | sed -e 's/\s$//g')
SEMESTER=$(echo "$SEMESTER" | sed -e 's/\s/_/g')
RAW_COURSES=$(echo "$RESULT" | grep -E "^\s*-.*$")
COURSES=$(echo "$RAW_COURSES" | sed -e 's/^\s*-\s*//g')
while IFS= read -r COURSE; do
  echo "Handling course $COURSE"
  dgc downloads add "$COURSE" "/downloads/$SEMESTER/$COURSE" --regex "$REGEX"
done <<< "$COURSES"

dgc pull;