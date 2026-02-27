---
tags: [embedded, arm, gpio, hal]
---

# Getting Started with STM32

STM32 microcontrollers are a family of 32-bit ARM Cortex-M based MCUs manufactured by STMicroelectronics. They are widely used in embedded systems, robotics, and IoT applications.

## Prerequisites

- STM32 development board (e.g., STM32F103C8T6 "Blue Pill")
- ST-Link V2 programmer
- STM32CubeIDE or PlatformIO

## GPIO Configuration

The GPIO pins can be configured in different modes. The output voltage can be calculated with a simple voltage divider:

$$V_{out} = V_{DD} \times \frac{R_2}{R_1 + R_2}$$

### Pin Modes

| Mode | Description |
|------|-------------|
| Input | Read digital signals |
| Output | Drive digital signals |
| Analog | ADC/DAC operations |
| Alternate Function | UART, SPI, I2C, etc. |

## Example: Blinking an LED

A minimal blink example using the HAL library:

```c
#include "stm32f1xx_hal.h"

int main(void) {
    HAL_Init();
    SystemClock_Config();

    __HAL_RCC_GPIOC_CLK_ENABLE();

    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = GPIO_PIN_13;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

    while (1) {
        HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);
        HAL_Delay(500);
    }
}
```

> [!tip] Quick Tip
> The onboard LED on most Blue Pill boards is connected to PC13 and is **active low**.

## Clock Configuration

The system clock frequency is derived from:

$f_{sys} = f_{HSE} \times \frac{PLL_N}{PLL_M \times PLL_P}$

where $f_{HSE}$ is the high-speed external oscillator frequency (typically 8 MHz).

> [!note] Note
> Always verify your clock configuration with the Clock Configuration tab in STM32CubeMX before flashing.

## UART Communication

To send data over UART, configure the baud rate using:

$$\text{Baud Rate} = \frac{f_{CK}}{16 \times \text{USARTDIV}}$$

```c
UART_HandleTypeDef huart1;

void UART_Init(void) {
    huart1.Instance = USART1;
    huart1.Init.BaudRate = 115200;
    huart1.Init.WordLength = UART_WORDLENGTH_8B;
    huart1.Init.StopBits = UART_STOPBITS_1;
    huart1.Init.Parity = UART_PARITY_NONE;
    huart1.Init.Mode = UART_MODE_TX_RX;
    HAL_UART_Init(&huart1);
}
```

> [!warning] Warning
> Make sure your ST-Link drivers are properly installed before attempting to flash the board.
