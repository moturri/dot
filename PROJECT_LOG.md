- **2025-10-29**: feat(widgets): refactor battery and brightctl widgets

  Refactors the battery and brightness control widgets for improved stability, performance, and adherence to event-driven principles.

  **Battery Widget:**
  - Stabilized the pyudev-based event monitoring.
  - Implemented graceful thread shutdown.
  - Debounced udev events to prevent UI flickering.
  - Improved logging and exception handling.

  **Brightness Widget:**
  - Migrated from GenPollText to TextBox, removing polling.
  - The widget is now fully event-driven, only updating on command.
  - This change reduces CPU usage and simplifies the widgets logic.

- **2025-10-29**: refine event-driven PipeWire widget for safety and cleanup

  Enhanced BaseAudioWidget while preserving zero-polling design.
  - Added thread join() in finalize() for clean Qtile reloads
  - Ensured safe termination of wpctl subscribe subprocesses
  - Highlighted overdrive volumes >100% with gold color
  - Improved inline documentation and clarified method contracts
  Widget remains fully event-driven, silent in idle state, and adheres
  to suckless minimalism and performance discipline.

- **2025-10-29**: battery: refactor and stabilize pyudev-based battery widget

  Improved the event-driven BatteryWidget built on GenPollText:
  - Added robust logging and structured exception handling
  - Implemented graceful thread shutdown via finalize()
  - Debounced rapid udev events for smoother UI updates
  - Refined icon and colour logic for consistent state display
  - Added full typing support and docstring clarity
  - Preserved zero-polling design for minimal CPU usage

- **2025-10-29**: brightctl_widget: migrate to TextBox for fully event-driven updates

  Refactored BrightctlWidget to subclass TextBox instead of GenPollText.
  Removed all polling mechanisms and periodic update intervals, making the
  widget strictly event-driven. Brightness changes and display updates are
  now triggered explicitly through exposed commands.

  This eliminates background CPU use, simplifies runtime behaviour, and
  aligns the widget with Arch/Suckless minimalism principles. Added a
  # type: ignore[no-untyped-call] directive to maintain mypy --strict
  compliance given untyped upstream Qtile base classes.

- **2025-10-29**: Updated `battery.py` to use only `pyudev`. Updated `README.md`.