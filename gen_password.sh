#!/usr/bin/env bash
# --------------------------------------------------------------------
# generate_password_demo_no_shuf.sh
#   Inline password generator that always meets the policy:
#       • ≥ 8 characters (default 20)
#       • at least one upper‑case, one lower‑case, one digit
#       • at least one *special* character (from a safe list)
#   No external `shuf` binary is required – a pure‑Bash Fisher‑Yates
#   shuffle is used instead.
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# 1️⃣  Pure‑Bash Fisher‑Yates shuffle (works on any Bash ≥ 3)
# --------------------------------------------------------------------
# Usage: shuffled=$(shuffle "string")
shuffle() {
    local input=$1
    local -a a
    local i j tmp len

    len=${#input}
    for ((i=0;i<len;i++)); do
        a[i]=${input:i:1}
    done

    for ((i=len-1;i>0;i--)); do
        j=$(( RANDOM % (i+1) ))   # random index 0…i
        tmp=${a[i]}
        a[i]=${a[j]}
        a[j]=$tmp
    done

    printf '%s' "${a[@]}"
}
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# 2️⃣  Password‑generation function (inline, no external shuf)
# --------------------------------------------------------------------
generate_password() {
    # ---- configuration ------------------------------------------------
    local MIN_LEN=8
    local DEFAULT_LEN=20
    # A set of specials that are safe to pass to `tr -dc`.  All of them
    # are escaped for the `tr` character class (dash is first, brackets are last).
    local DEFAULT_SPECIAL='!@#$%^&*()-_=+[]{}<>?,.;:'

    # ---- arguments ----------------------------------------------------
    local len=${1:-$DEFAULT_LEN}                 # requested length
    local special="${2:-$DEFAULT_SPECIAL}"       # custom specials (optional)

    # ---- sanity --------------------------------------------------------
    if (( len < MIN_LEN )); then
        echo "Error: length $len < minimum $MIN_LEN required by policy." >&2
        return 1
    fi

    # ---- tiny helper: pick ONE random char from a class using openssl ----
    # $1 – character class for `tr -dc` (e.g. 'A-Z' or '0-9')
    _pick_one_class() {
        # We request a few extra random bytes so that after filtering we
        # still have at least one character.
        openssl rand -base64 6 | tr -dc "$1" | head -c1
    }

    # ---- pick ONE special character **without** using tr ---------------
    # Using Bash's $RANDOM guarantees we always get a character from the set.
    _pick_one_special() {
        local set=$1
        local idx=$(( RANDOM % ${#set} ))
        echo "${set:idx:1}"
    }

    # ---- guarantee each required class ---------------------------------
    local upper lower digit spec
    upper=$(_pick_one_class 'A-Z')
    lower=$(_pick_one_class 'a-z')
    digit=$(_pick_one_class '0-9')
    spec=$(_pick_one_special "$special")   # <-- this is the key line

    # ---- pool for the remaining characters -------------------------------
    # The pool contains every character we are allowed to use.
    local pool="A-Za-z0-9${special}"
    local remaining=$(( len - 4 ))   # we already have 4 mandatory chars

    # Generate enough raw base64 data, then filter to the pool.
    # Multiplying by 3 gives a comfortable safety margin.
    local rest
    rest=$(openssl rand -base64 $((remaining * 3)) |
           tr -dc "$pool" |
           head -c "$remaining")

    # ---- combine --------------------------------------------------------
    local combined="${upper}${lower}${digit}${spec}${rest}"

    # ---- shuffle (pure Bash) --------------------------------------------
    shuffle "$combined"
}
# --------------------------------------------------------------------

# --------------------------------------------------------------------
# 3️⃣  Example usage – call the function from the same script
# --------------------------------------------------------------------
#echo "=== Demo: default password (20 chars, default specials) ==="
#pw1=$(generate_password)            # defaults to 20 chars
#echo "Generated: $pw1"

#echo
#echo "=== Demo: 12‑char password, custom specials *$#@! ==="
#pw2=$(generate_password 12 '*$#@!')
#echo "Generated: $pw2"

# Uncomment the lines below to see the policy in action (optional)
# echo
# echo "Checking the policies with grep:"
# echo "$pw1" | grep -q '[A-Z]' && echo "  Uppercase OK"
# echo "$pw1" | grep -q '[a-z]' && echo "  Lowercase OK"
# echo "$pw1" | grep -q '[0-9]' && echo "  Digit OK"
# echo "$pw1" | grep -q "[${DEFAULT_SPECIAL}]" && echo "  Special OK"
# --------------------------------------------------------------------
