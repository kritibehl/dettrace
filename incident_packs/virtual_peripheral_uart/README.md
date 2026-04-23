# Virtual Peripheral Replay Pack

This pack adds a firmware-style validation scenario to DetTrace using a simulated UART TX interrupt flow.

It is not hardware emulation.

It is trace-driven replay of hardware/software interaction events such as:
- register_write
- register_read
- irq_assert
- irq_clear
- isr_enter
- isr_exit
- tx_fifo_empty
- tx_fifo_push

Scenarios:
- uart_interrupt_nominal
- uart_interrupt_stuck_irq
