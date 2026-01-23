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
# Available custom modes (defined in xorg.conf)
# -----------------------------
CUSTOM_MODES=("1920x1080_60.00" "1800x1012_60.00")

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
# Cache xrandr output to avoid multiple calls
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

	# Check if custom modes are available for the display
	for mode_name in "${CUSTOM_MODES[@]}"; do
		if ! echo "$XRANDR_OUTPUT" | grep -A50 "^$display connected" | grep -q "$mode_name"; then
			notify-send "Display Setup" "Warning: Mode $mode_name not available on $display" -u normal
		fi
	done
}

restart_qtile() {
	sleep 1
	if pgrep -x qtile >/dev/null 2>&1; then
		qtile cmd-obj -o cmd -f restart >/dev/null 2>&1 ||
			notify-send "Display Setup" "Qtile restart failed; restart manually if needed." -t 6000
	fi
}

disconnect_all_externals() {
	for ext in "${EXTERNALS[@]}"; do
		if is_connected "$ext"; then
			xrandr --output "$ext" --off 2>/dev/null || true
		fi
	done
	xrandr --output "$INTERNAL" --primary --auto
	notify-send "Display Setup" "All external displays disconnected." -t 6000
	restart_qtile
}

configure_internal_display() {
	verify_modes_available "$INTERNAL"

	local mode
	mode=$(printf "1920x1080_60.00\n1800x1012_60.00\nAuto (default)\n" | rofi -dmenu -i -p "Internal Display Resolution") || exit 0

	case "$mode" in
	"Auto (default)")
		xrandr --output "$INTERNAL" --primary --auto
		;;
	*)
		if xrandr --output "$INTERNAL" --primary --mode "$mode" 2>/dev/null; then
			notify-send "Display Setup" "Internal display configured to $mode." -t 6000
		else
			notify-send "Display Setup" "Failed to set $mode. Using auto mode." -u normal
			xrandr --output "$INTERNAL" --primary --auto
		fi
		;;
	esac

	restart_qtile
}

configure_external_display() {
	local display="$1"

	# Disable other external displays
	for ext in "${EXTERNALS[@]}"; do
		if [ "$ext" != "$display" ] && is_connected "$ext"; then
			xrandr --output "$ext" --off 2>/dev/null || true
		fi
	done

	# Select position
	local position
	position=$(printf "Left of internal\nRight of internal\nAbove internal\nBelow internal\n" | rofi -dmenu -i -p "Position") || exit 0

	local xrandr_pos
	case "$position" in
	"Left of internal") xrandr_pos="--left-of" ;;
	"Right of internal") xrandr_pos="--right-of" ;;
	"Above internal") xrandr_pos="--above" ;;
	"Below internal") xrandr_pos="--below" ;;
	*) exit 0 ;;
	esac

	# DP-1 always uses auto/native resolution
	if [ "$display" = "$DP" ]; then
		if xrandr --output "$display" --auto "$xrandr_pos" "$INTERNAL" 2>/dev/null; then
			notify-send "Display Setup" "$display configured with native resolution ($position)." -t 6000
		else
			notify-send "Display Setup" "Failed to configure $display." -u critical
			exit 1
		fi
	else
		# For HDMI, verify custom modes and allow selection
		verify_modes_available "$display"

		local mode
		mode=$(printf "1920x1080\n1800x1012_60.00\nAuto (native)\n" | rofi -dmenu -i -p "Resolution") || exit 0

		case "$mode" in
		"Auto (native)")
			if xrandr --output "$display" --auto "$xrandr_pos" "$INTERNAL" 2>/dev/null; then
				notify-send "Display Setup" "$display configured with native resolution ($position)." -t 6000
			else
				notify-send "Display Setup" "Failed to configure $display." -u critical
				exit 1
			fi
			;;
		*)
			if xrandr --output "$display" --mode "$mode" "$xrandr_pos" "$INTERNAL" 2>/dev/null; then
				notify-send "Display Setup" "$display configured to $mode ($position)." -t 6000
			else
				notify-send "Display Setup" "Failed to configure $display with $mode. Trying auto mode..." -u normal
				xrandr --output "$display" --auto "$xrandr_pos" "$INTERNAL"
				notify-send "Display Setup" "$display configured with auto mode ($position)." -t 6000
			fi
			;;
		esac
	fi

	restart_qtile
}

# -----------------------------
# Main
# -----------------------------
main() {
	local choices=()

	# Add internal display option
	choices+=("eDP-1 (Internal)")

	# Add connected external displays
	is_connected "$HDMI" && choices+=("HDMI-1")
	is_connected "$DP" && choices+=("DP-1")

	# Always offer disconnect option
	choices+=("Disconnect external displays")

	# Select display
	local selection
	selection=$(printf '%s\n' "${choices[@]}" | "${ROFI_CMD[@]}") || exit 0

	case "$selection" in
	"Disconnect external displays")
		disconnect_all_externals
		exit 0
		;;
	"eDP-1 (Internal)")
		configure_internal_display
		exit 0
		;;
	"HDMI-1")
		configure_external_display "$HDMI"
		;;
	"DP-1")
		configure_external_display "$DP"
		;;
	*)
		exit 0
		;;
	esac
}

main
