# Firmware Trace Replay Pack

DetTrace replays firmware-style trace sequences without claiming hardware emulation.

Scenarios:
- uart_stuck_interrupt
- timer_missed_tick
- gpio_interrupt_race
- register_write_ordering_mismatch

Event model:
- register_write
- register_read
- irq_assert
- irq_clear
- isr_enter
- isr_exit
- tick_fire
- tick_miss
- gpio_edge
- gpio_ack

What DetTrace isolates:
- first divergence index
- expected vs actual event
- stale status bit
- missing irq_clear
- wrong ordering
- missed tick
