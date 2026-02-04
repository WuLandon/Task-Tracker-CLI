Output demo.gif

Require "tasker"

# Settings
Set Shell "bash"
Set FontSize 14
Set WindowBar Colorful
Set LineHeight 1.6
Set Padding 15
Set Width 1050
Set Height 500
Set TypingSpeed 100ms

# --- Demo starts ---
Type "tasker -h" Sleep 300ms Enter Sleep 3s

# Add tasks
Type "tasker add 'buy bread'" Sleep 300ms Enter Sleep 900ms
Type "tasker add 'finish reviewing new documentation'" Sleep 300ms Enter Sleep 900ms
Type "tasker add 'look for a recipe to cook'" Sleep 300ms Enter Sleep 900ms

# List all tasks
Type "tasker list" Sleep 300ms Enter Sleep 2s

# Update description, mark statuses
Type "tasker update 1 --description 'buy sourdough bread'" Sleep 300ms Enter Sleep 900ms
Type "tasker mark-done 2" Sleep 300ms Enter Sleep 900ms
Type "tasker mark-in-progress 3" Sleep 300ms Enter Sleep 900ms

# List filters
Type "tasker list --task-id 1" Sleep 300ms Enter Sleep 900ms
Type "tasker list --status in-progress" Sleep 300ms Enter Sleep 900ms
Type "tasker list --status done" Sleep 300ms Enter Sleep 900ms

# Delete
Type "tasker delete 1" Sleep 300ms Enter Sleep 900ms

# Date filter
Type "tasker list --date '=2026-02'" Sleep 300ms Enter

Sleep 5s
