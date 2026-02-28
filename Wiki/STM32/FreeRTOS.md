---
title: FreeRTOS Startup
date: 2026-02-27
tags: [FreeRTOS, hal]
---

# OS

There are two main types of OS: GPOS and RTOS. GPOS, which stands for general purpose operating system, e.g. windows 11, MAC OS; and for RTOS, which means real time operating system, includes FreeRTOS, Vxworks etc.   

The GPOS mainly optimized for throughput and user experience, not timing, the scheduler will prioritize overall system responsiveness, not determinism. While RTOS optimized for deterministic timing, this is critical for controllers, missed deadline for such timing will cause physical failure.  

# FreeRTOS

FreeRTOS is a class of RTOS designed to run on microcontrollers, it provides core real time scheduling functionality, inter-task communication, timing and synchronization. This allows it able to use in robotices, automotive projects.  

# Setup FreeRTOS
To start up with FreeRTOS, I have selected STM32H723ZG nucleo board, which is a very powerful H7 chip that can do a lot of things.  
Here is a step by step tutorial to start with it:  

## Step 1: Installation
![RTOS selection](pic/RTOS%20selection.png)
1) Select FREERTOS on the left bar in "Middleware and Software Packs" section, for interface, select "CMSIS_V2" here, CMSIS_V2 is the newer standard and generally recommended, it is also cleaner and more portable. Keep all other settings unchanged for current stage.  
   
   *CMSIS is a wrapper API for FreeRTOS, e.g. original FreeRTOS API: xTaskCreate() -> wrapped API: osThreadNew() etc.*   

2) Keep the clock configuration with MAX frequency, in my case 275MHz.
3) In "System Core" -> "SYS" section, change the timebase source from "Systick" to other timer, for here I select TIM 6 as an example. Changing is required since normally Systick is used to power HAL based lib functions like `HAL_Delay()`; whereas, freertos needs Systick for its own `SysTick_Handler`, if both of them using the same Systick, they will fight over the same interrupt handler which leads to things break.
   ![[timer Selection.png]]
4) In "Project manager", use Makefile as Toolchain, and for "Code Generator", select like this will be sufficient: ![Code Gen RTOS](pic/Code%20Gen%20RTOS.png)

Once generated, we are almost all done, in the `main.c` file, we can see some different compared to normal MCU one: 
```C
osKernelInitialize();
MX_FREERTOS_Init();
```

This is where RTOS starts working, all remaining code behind will not be executed, for example the `while(1)`. Everything now will start running in `freertos.c`.

## Step 2: Turn on a LED
In `freertos.c` we can see once the `MX_FREERTOS_Init()` was called, it will then stay in this OS and never get out, the main loop now in FreeRTOS becomes: `for(;;)`:
```C
void StartDefaultTask(void *argument)
{
  /* USER CODE BEGIN StartDefaultTask */
  /* Infinite loop */
  for(;;)
  {
  
  }
  /* USER CODE END StartDefaultTask */
}
```

So here if we try to turn on the LED:
```C
void StartDefaultTask(void *argument)
{
  /* USER CODE BEGIN StartDefaultTask */
  /* Infinite loop */
  for(;;)
  {
    HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_0);
    osDelay(500);
  }
  /* USER CODE END StartDefaultTask */
}
```
This code will make a blinky LED!