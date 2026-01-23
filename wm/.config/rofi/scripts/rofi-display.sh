#!/usr/bin/env bash
set -euo pipefail

# -----------------------------
# Display identifiers
# -----------------------------
INTERNAL="eDP-1"
HDMI="HDMI-1"
DP="DP-1"
EXTERNALS=("$HDMI" "$DP")

# -----------------------------
# Custom modes (defined in xorg.conf)
# -----------------------------
REDUCED_MODES=("1920x1080R" "1800x1012R")
FULL_MODES=("1920x1080_60.00" "1800x1012_60.00")
ALL_CUSTOM_MODES=("${REDUCED_MODES[@]}" "${FULL_MODES[@]}")

# -----------------------------
# Rofi
# -----------------------------
ROFI_CMD=(rofi -dmenu -i -p "Display")

# -----------------------------
# Dependency check
# -----------------------------
for cmd in xrandr notify-send rofi qtile; do
	command -v "$cmd" >/dev/null 2>&1 || {
		notify-send "Display Setup" "Missing required command: $cmd" -u critical
		exit 1
	}
done

# -----------------------------
# Cache xrandr output
# -----------------------------
XRANDR_OUTPUT=$(xrandr)

# -----------------------------
# Helpers
# -----------------------------
is_connected() {
	echo "$XRANDR_OUTPUT" | grep -q "^$1 connected"
}

verify_modes_available() {
	local display="$1"
	for mode in "${ALL_CUSTOM_MODES[@]}"; do
		if ! echo "$XRANDR_OUTPUT" |
			grep -A50 "^$display connected" |
			grep -q "$mode"; then
			notify-send "Display Setup" \
				"Warning: Mode $mode not available on $display" -u normal
		fi
	done
}

restart_qtile() {
	sleep 1
	if pgrep -x qtile >/dev/null 2>&1; then
		qtile cmd-obj -o cmd -f restart >/dev/null 2>&1 ||
			notify-send "Display Setup" \
				"Qtile restart failed; restart manually if needed." -t 6000
	fi
}

disconnect_all_externals() {
	for ext in "${EXTERNALS[@]}"; do
		is_connected "$ext" && xrandr --output "$ext" --off 2>/dev/null || true
	done
	xrandr --output "$INTERNAL" --primary --auto
	notify-send "Display Setup" "All external displays disconnected." -t 6000
	restart_qtile
}

# -----------------------------
# Internal display
# -----------------------------
configure_internal_display() {
	verify_modes_available "$INTERNAL"

	local menu
	menu=$(printf "%s\n" \
		"${REDUCED_MODES[@]}" \
		"${FULL_MODES[@]}" \
		"Auto (default)")

	local mode
	mode=$(echo "$menu" | rofi -dmenu -i -p "Internal Display Resolution") || exit 0

	if [ "$mode" = "Auto (default)" ]; then
		xrandr --output "$INTERNAL" --primary --auto
	else
		xrandr --output "$INTERNAL" --primary --mode "$mode" 2>/dev/null || {
			notify-send "Display Setup" \
				"Failed to set $mode. Falling back to auto." -u normal
			xrandr --output "$INTERNAL" --primary --auto
		}
	fi

	restart_qtile
}

# -----------------------------
# External display
# -----------------------------
configure_external_display() {
	local display="$1"

	for ext in "${EXTERNALS[@]}"; do
		[ "$ext" != "$display" ] && is_connected "$ext" &&
			xrandr --output "$ext" --off 2>/dev/null || true
	done

	local position
	position=$(printf "Left of internal\nRight of internal\nAbove internal\nBelow internal\n" |
		rofi -dmenu -i -p "Position") || exit 0

	local xrandr_pos
	case "$position" in
	"Left of internal") xrandr_pos="--left-of" ;;
	"Right of internal") xrandr_pos="--right-of" ;;
	"Above internal") xrandr_pos="--above" ;;
	"Below internal") xrandr_pos="--below" ;;
	*) exit 0 ;;
	esac

	# DP always uses native timing
	if [ "$display" = "$DP" ]; then
		xrandr --output "$display" --auto "$xrandr_pos" "$INTERNAL" 2>/dev/null ||
			notify-send "Display Setup" "Failed to configure $display." -u critical
		restart_qtile
		return
	fi

	# HDMI: allow reduced + full modes
	verify_modes_available "$display"

	local menu
	menu=$(printf "%s\n" \
		"${REDUCED_MODES[@]}" \
		"1920x1080" \
		"${FULL_MODES[@]}" \
		"Auto (native)")

	local mode
	mode=$(echo "$menu" | rofi -dmenu -i -p "Resolution") || exit 0

	if [ "$mode" = "Auto (native)" ]; then
		xrandr --output "$display" --auto "$xrandr_pos" "$INTERNAL"
	else
		xrandr --output "$display" --mode "$mode" \
			"$xrandr_pos" "$INTERNAL" 2>/dev/null || {
			notify-send "Display Setup" \
				"Failed to set $mode. Falling back to auto." -u normal
			xrandr --output "$display" --auto "$xrandr_pos" "$INTERNAL"
		}
	fi

	restart_qtile
}

# -----------------------------
# Main
# -----------------------------
main() {
	local choices=("eDP-1 (Internal)")

	is_connected "$HDMI" && choices+=("HDMI-1")
	is_connected "$DP" && choices+=("DP-1")

	choices+=("Disconnect external displays")

	local selection
	selection=$(printf "%s\n" "${choices[@]}" | "${ROFI_CMD[@]}") || exit 0

	case "$selection" in
	"Disconnect external displays") disconnect_all_externals ;;
	"eDP-1 (Internal)") configure_internal_display ;;
	"HDMI-1") configure_external_display "$HDMI" ;;
	"DP-1") configure_external_display "$DP" ;;
	esac
}

main
