#ifndef _MLX90640_SHIELD_H_
#define _MLX90640_SHIELD_H_

#include <stdint.h>
#include <Arduino.h>

#define LEDPIN7 25
#define LEDPIN6 26
#define LEDPIN5 27
#define LEDPIN4 14
#define LEDPIN3 16
#define LEDPIN2 4
#define LEDPIN1 2
#define LEDPIN0 15

void MLX90640_Shield_setup();
int MLX90640_Shield_WriteByte(uint8_t byte);

#endif