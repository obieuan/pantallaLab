// DECLARA LAS VARIABLES DE COMUNICACION SERIAL
char RX;
String mensaje = "";
bool RELE_1_STATE = 1;
bool RELE_2_STATE = 1;

// DEFINE LOS PÍNES DIGITALES POR EL NOMBRE Y NUMERO DEL RELE
#define RELE_1 2
#define RELE_2 3
#define RELE_3 4
#define RELE_4 5
#define RELE_5 6
#define RELE_6 7
#define RELE_7 8
#define RELE_8 9
#define RELE_9 31
#define RELE_10 33
#define RELE_11 35
#define RELE_12 37
#define RELE_13 39
#define RELE_14 41
#define RELE_15 43
#define RELE_16 45

// CICLO DE INICIO, DECLARA ENTRADAS/SALIDAS Y ESTADOS INICIALES
void setup() {
  Serial.begin(9600);  // Comunicacion serial a 9600 baudios

  // Declara los pines de los reles como salidas
  pinMode(RELE_1, OUTPUT);
  pinMode(RELE_2, OUTPUT);
  pinMode(RELE_3, OUTPUT);
  pinMode(RELE_4, OUTPUT);
  pinMode(RELE_5, OUTPUT);
  pinMode(RELE_6, OUTPUT);
  pinMode(RELE_7, OUTPUT);
  pinMode(RELE_8, OUTPUT);
  pinMode(RELE_9, OUTPUT);
  pinMode(RELE_10, OUTPUT);
  pinMode(RELE_11, OUTPUT);
  pinMode(RELE_12, OUTPUT);
  pinMode(RELE_13, OUTPUT);
  pinMode(RELE_14, OUTPUT);
  pinMode(RELE_15, OUTPUT);
  pinMode(RELE_16, OUTPUT);

  // Inicia los pines de salida en uno, lo que apaga los reles activos en bajo
  ALL_OFF();
}

void loop() {
  // Comprueba si hay una señal serial de entrada
  while (Serial.available() > 0) {
    RX = Serial.read();
    if (RX == '\n') {
      procesar_mensaje(mensaje);
      mensaje = "";
    } else {
      mensaje += RX;
    }
  }
}

// Procesa el mensaje recibido
void procesar_mensaje(String mensaje) {
  // El mensaje tiene el formato "%,mesa_id,estado"
  if (mensaje.startsWith("%")) {
    mensaje.remove(0, 1); // Elimina el caracter "%"
    int index1 = mensaje.indexOf(',');
    int index2 = mensaje.lastIndexOf(',');

    if (index1 > 0 && index2 > index1) {
      String mesa_id = mensaje.substring(index1 + 1, index2);
      String estado = mensaje.substring(index2 + 1);

      int mesa = mesa_id.toInt();
      int estado_int = estado.toInt();

      if (estado_int == 1) {
        Serial.print("Encendiendo mesa: ");
        Serial.println(mesa);
        encender_rele(mesa);
      } else if (estado_int == 0) {
        Serial.print("Apagando mesa: ");
        Serial.println(mesa);
        apagar_rele(mesa);
      }
    }
  }
}

// Enciende el rele correspondiente a la mesa
void encender_rele(int mesa) {
  switch (mesa) {
    case 1: digitalWrite(RELE_1, LOW); break;
    case 2: digitalWrite(RELE_2, LOW); break;
    case 3: digitalWrite(RELE_3, LOW); break;
    case 4: digitalWrite(RELE_4, LOW); break;
    case 5: digitalWrite(RELE_5, LOW); break;
    case 6: digitalWrite(RELE_6, LOW); break;
    case 7: digitalWrite(RELE_7, LOW); break;
    case 8: digitalWrite(RELE_8, LOW); break;
    case 9: digitalWrite(RELE_9, LOW); break;
    case 10: digitalWrite(RELE_10, LOW); break;
    case 11: digitalWrite(RELE_11, LOW); break;
    case 12: digitalWrite(RELE_12, LOW); break;
    case 13: digitalWrite(RELE_13, LOW); break;
    case 14: digitalWrite(RELE_14, LOW); break;
    case 15: digitalWrite(RELE_15, LOW); break;
    case 16: digitalWrite(RELE_16, LOW); break;
    default: break;
  }
}

// Apaga el rele correspondiente a la mesa
void apagar_rele(int mesa) {
  switch (mesa) {
    case 1: digitalWrite(RELE_1, HIGH); break;
    case 2: digitalWrite(RELE_2, HIGH); break;
    case 3: digitalWrite(RELE_3, HIGH); break;
    case 4: digitalWrite(RELE_4, HIGH); break;
    case 5: digitalWrite(RELE_5, HIGH); break;
    case 6: digitalWrite(RELE_6, HIGH); break;
    case 7: digitalWrite(RELE_7, HIGH); break;
    case 8: digitalWrite(RELE_8, HIGH); break;
    case 9: digitalWrite(RELE_9, HIGH); break;
    case 10: digitalWrite(RELE_10, HIGH); break;
    case 11: digitalWrite(RELE_11, HIGH); break;
    case 12: digitalWrite(RELE_12, HIGH); break;
    case 13: digitalWrite(RELE_13, HIGH); break;
    case 14: digitalWrite(RELE_14, HIGH); break;
    case 15: digitalWrite(RELE_15, HIGH); break;
    case 16: digitalWrite(RELE_16, HIGH); break;
    default: break;
  }
}

// Apaga todos los reles, estos son activos en bajo
void ALL_OFF() {
  digitalWrite(RELE_1, HIGH);
  digitalWrite(RELE_2, HIGH);
  digitalWrite(RELE_3, HIGH);
  digitalWrite(RELE_4, HIGH);
  digitalWrite(RELE_5, HIGH);
  digitalWrite(RELE_6, HIGH);
  digitalWrite(RELE_7, HIGH);
  digitalWrite(RELE_8, HIGH);
  digitalWrite(RELE_9, HIGH);
  digitalWrite(RELE_10, HIGH);
  digitalWrite(RELE_11, HIGH);
  digitalWrite(RELE_12, HIGH);
  digitalWrite(RELE_13, HIGH);
  digitalWrite(RELE_14, HIGH);
  digitalWrite(RELE_15, HIGH);
  digitalWrite(RELE_16, HIGH);
}

void ALL_ON() {
  digitalWrite(RELE_1, LOW);
  digitalWrite(RELE_2, LOW);
  digitalWrite(RELE_3, LOW);
  digitalWrite(RELE_4, LOW);
  digitalWrite(RELE_5, LOW);
  digitalWrite(RELE_6, LOW);
  digitalWrite(RELE_7, LOW);
  digitalWrite(RELE_8, LOW);
  digitalWrite(RELE_9, LOW);
  digitalWrite(RELE_10, LOW);
  digitalWrite(RELE_11, LOW);
  digitalWrite(RELE_12, LOW);
  digitalWrite(RELE_13, LOW);
  digitalWrite(RELE_14, LOW);
  digitalWrite(RELE_15, LOW);
  digitalWrite(RELE_16, LOW);
}
