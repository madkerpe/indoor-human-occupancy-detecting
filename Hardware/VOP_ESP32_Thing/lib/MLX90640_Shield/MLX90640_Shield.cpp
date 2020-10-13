#include <MLX90640_Shield.h>

void MLX90640_Shield_setup() {
    /*
    pinMode(LEDPIN0, OUTPUT);
    pinMode(LEDPIN1, OUTPUT);
    pinMode(LEDPIN2, OUTPUT);
    pinMode(LEDPIN3, OUTPUT);
    pinMode(LEDPIN4, OUTPUT);
    pinMode(LEDPIN5, OUTPUT);
    pinMode(LEDPIN6, OUTPUT);
    pinMode(LEDPIN7, OUTPUT);
    */
}

int MLX90640_Shield_WriteByte(uint8_t byte) {
    /*
    digitalWrite(LEDPIN1, LOW);
    digitalWrite(LEDPIN2, LOW);
    digitalWrite(LEDPIN3, LOW);
    digitalWrite(LEDPIN4, LOW);
    digitalWrite(LEDPIN5, LOW);
    digitalWrite(LEDPIN6, LOW);
    digitalWrite(LEDPIN7, LOW);
    digitalWrite(LEDPIN0, LOW);

    if (byte/128) {
        digitalWrite(LEDPIN0, HIGH);
    }
    byte = byte%128;

    if (byte/64) {
        digitalWrite(LEDPIN1, HIGH);
    }
    byte = byte%64;

    if (byte/32) {
        digitalWrite(LEDPIN2, HIGH);
    }
    byte = byte%32;

    if (byte/16) {
        digitalWrite(LEDPIN3, HIGH);
    }
    byte = byte%16;

    if (byte/8) {
        digitalWrite(LEDPIN4, HIGH);
    }
    byte = byte%8;

    if (byte/4) {
        digitalWrite(LEDPIN5, HIGH);
    }
    byte = byte%4;

    if (byte/2) {
        digitalWrite(LEDPIN6, HIGH);
    }
    byte = byte%2;

    if (byte) {
        digitalWrite(LEDPIN7, HIGH);
    }
    */
    return 0;
}