#include <Arduino.h>
//DEFINE LOS PÍNES DIGITALES POR EL NOMBRE Y NUMERO DEL RELE --------------------------------
#define RELE_4 2  //mesa 1
#define RELE_5 3  //mesa 2
#define RELE_6 4  //mesa 3
#define RELE_1 5  //mesa 4
#define RELE_2 6  //mesa 5
#define RELE_3 7  //mesa 6
#define RELE_13 8  //mesa 13
#define RELE_14 9  //mesa 14
#define RELE_15 31 //mesa --
#define RELE_10 33  //mesa --
#define RELE_11 35  //mesa 8
#define RELE_12 37  //mesa 9
#define RELE_7 39  //mesa -- 
#define RELE_8 41  //mesa ack
#define RELE_9 43  //mesa 15
#define RELE_16 45  //mesa 16

// Definir los pines de los relés en un array para facilitar su control
const int RELAYS[] = {RELE_1, RELE_2, RELE_3, RELE_4, RELE_5, RELE_6, RELE_7, RELE_8, RELE_9, RELE_10, RELE_11, RELE_12, RELE_13, RELE_14, RELE_15, RELE_16};

char RX = ' ';
char TX = ' ';
bool RELE_1_STATE = 1;
bool RELE_2_STATE = 1;
String msg;
char mesas[14][2];  // Suponiendo que hay 14 mesas

void setup() {
  Serial.begin(9600);
  // Configurar los pines de los relés como salidas
  for (int i = 0; i < 16; i++) {
    pinMode(RELAYS[i], OUTPUT);
  }

  ALL_OFF();
}

void loop() {
  readSerialPort();

  if (msg != "") {
    extractMesas();
    sendData();
    msg = "";
  }
  updateRelays();
  delay(500);
}

void readSerialPort() {
  if (Serial.available()) {
    delay(10);  // Pequeña pausa para permitir que llegue toda la data
    while (Serial.available() > 0) {
      char inChar = (char)Serial.read();
      msg += inChar;
    }
    Serial.flush();  // Limpia el buffer serial

  }
}

void ALL_OFF() {
  for (int i = 0; i < 16; i++) {
    digitalWrite(RELAYS[i], HIGH);  // Apagar todos los relés (HIGH = apagado en este caso)
  }
}

void extractMesas() {
  int start = msg.indexOf('&') + 1;
  int end = msg.indexOf('%');
  if (start < 0 || end < 0) return;  // Verifica delimitadores

  String data = msg.substring(start, end);
  int idx = 0;  // Índice para la matriz mesas

  int pos = 0;  // Posición en la cadena data
  while (pos < data.length()) {
    int sep = data.indexOf(',', pos);
    int next = data.indexOf(';', sep);
    if (sep < 0 || next < 0) break;

    String mesaNum = data.substring(pos, sep);          // Número de mesa
    String mesaEstado = data.substring(sep + 1, next);  // Estado de la mesa

    mesas[idx][0] = mesaNum.toInt();       // Convertir a entero si es necesario
    mesas[idx][1] = mesaEstado.charAt(0);  // Guardar el estado como char

    pos = next + 1;
    idx++;
  }
}

// Función para actualizar los relés en función del estado de las mesas
void updateRelays() {
  for (int i = 0; i < 14; i++) {  // Iterar por las mesas
    if (mesas[i][1] == '1') {
      digitalWrite(RELAYS[i], LOW);  // Activar el relé (LOW = activado)
    } else {
      digitalWrite(RELAYS[i], HIGH);  // Desactivar el relé (HIGH = apagado)
    }
  }
}

void sendData() {
  Serial.print("ACK");
}
