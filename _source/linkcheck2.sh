#!/bin/bash
# Parallel external-link checker for the whole site.
# Null-delimited so URLs containing quotes or apostrophes (common in French
# Wikipedia titles) cannot break the pipeline.
cd /Users/bellum/claude-dir/hors-de-la-caverne || exit 1
grep -oh 'href="https\?://[^"]*"' ./*.html | sed 's/^href="//; s/"$//' | sort -u > /tmp/hdlc_urls.txt
echo "unique external URLs: $(wc -l < /tmp/hdlc_urls.txt)"
check() {
  url="$1"
  UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 20 -L -A "$UA" --head "$url")
  case "$code" in 2*|3*) return;; esac
  code=$(curl -s -o /dev/null -w '%{http_code}' -m 25 -L -A "$UA" -r 0-2048 "$url")
  case "$code" in 2*|3*) return;; esac
  echo "BAD $code $url"
}
export -f check
tr '\n' '\0' < /tmp/hdlc_urls.txt | xargs -0 -P 12 -I{} bash -c 'check "$@"' _ {}
echo "DONE"
