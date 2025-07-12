#!/usr/bin/env bash
set -euo pipefail

LOCK_CMD="${LOCK_CMD:-}"
if [[ -z "$LOCK_CMD" ]]; then
	for cmd in i3lock betterlockscreen xlock swaylock; do
		if command -v "$cmd" &>/dev/null; then
			LOCK_CMD="$cmd"
			break
		fi
	done
fi

ROFI_CMD="rofi -dmenu -i -p"
TITLE_ICON="󰟀 "
LOCK_ICON="󰌾  Lock"
SLEEP_ICON="󰒲  Sleep"
LOGOUT_ICON="  Logout"
REBOOT_ICON="󱑞  Reboot"
SHUTDOWN_ICON="󰐥  Shutdown"
CANCEL_ICON="󰜺  Cancel"

options=(
	"$LOCK_ICON"
	"$SLEEP_ICON"
	"$LOGOUT_ICON"
	"$REBOOT_ICON"
	"$SHUTDOWN_ICON"
	"$CANCEL_ICON"
)

choice=$(printf '%s\n' "${options[@]}" | $ROFI_CMD "$TITLE_ICON" -lines "${#options[@]}" || exit 1)

confirm_action() {
	local prompt="$1"
	echo -e "Yes\nNo" | $ROFI_CMD "$prompt"
}

logout_session() {
	if pgrep -x qtile &>/dev/null; then
		qtile cmd-obj -o cmd -f logout
	elif pgrep -x dwm &>/dev/null; then
		pkill dwm
	fi
}

lock_system() {
	case "$LOCK_CMD" in
	i3lock)
		i3lock -c 000000
		;;
	*)
		notify-send "Power Menu " " i3lock command not found in PATH."
		;;
	esac
}

case "$choice" in
"$LOCK_ICON")
	lock_system
	;;
"$SLEEP_ICON")
	[[ "$(confirm_action '󰒲  Suspend system?')" == "Yes" ]] && systemctl suspend
	;;
"$LOGOUT_ICON")
	[[ "$(confirm_action '  Logout?')" == "Yes" ]] && logout_session
	;;
"$REBOOT_ICON")
	[[ "$(confirm_action '󱑞  Reboot system?')" == "Yes" ]] && systemctl reboot
	;;
"$SHUTDOWN_ICON")
	[[ "$(confirm_action '󰐥  Power off system?')" == "Yes" ]] && systemctl poweroff
	;;
"$CANCEL_ICON" | *)
	exit 0
	;;
esac
