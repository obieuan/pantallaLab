//DECLARA LAS VARIABLES DE COMUNICACION SERIAL ----------------------------------------------
char RX = ' ';
char TX = ' ';
bool RELE_1_STATE = 1;
bool RELE_2_STATE = 1;

//DEFINE LOS PÍNES DIGITALES POR EL NOMBRE Y NUMERO DEL RELE --------------------------------
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

//CICLO DE INICIO, DECLARA ENTRADAS/SALIDAS Y ESTADOS INICIALES -----------------------------
void setup() {
  Serial.begin(9600);  //Comunicacion serial a 9600 baudios

  //Declara los pines de los reles como salidas
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

  //Inicia los pines de salida en uno, lo que apaga los reles activos en bajo
  ALL_OFF();

  // Enciende los relés secuencialmente
  turnOnRelaysSequentially();
}

void loop() {
  // El loop queda vacío ya que no necesitamos hacer nada más en él.
}

//APAGA TODOS LOS RELES, ESTOS SON ACTIVOS EN BAJO
void ALL_OFF() {
  digitalWrite(RELE_1, 1);
  digitalWrite(RELE_2, 1);
  digitalWrite(RELE_3, 1);
  digitalWrite(RELE_4, 1);
  digitalWrite(RELE_5, 1);
  digitalWrite(RELE_6, 1);
  digitalWrite(RELE_7, 1);
  digitalWrite(RELE_8, 1);
  digitalWrite(RELE_9, 1);
  digitalWrite(RELE_10, 1);
  digitalWrite(RELE_11, 1);
  digitalWrite(RELE_12, 1);
  digitalWrite(RELE_13, 1);
  digitalWrite(RELE_14, 1);
  digitalWrite(RELE_15, 1);
  digitalWrite(RELE_16, 1);
}

void turnOnRelaysSequentially() {
  int relays[] = {RELE_1, RELE_2, RELE_3, RELE_4, RELE_5, RELE_6, RELE_7, RELE_8, RELE_9, RELE_10, RELE_11, RELE_12, RELE_13, RELE_14, RELE_15, RELE_16};
  for (int i = 0; i < 16; i++) {
    digitalWrite(relays[i], 0); // Enciende el relé
    delay(1000); // Espera 1 segundo
  }
}

void ALL_ON() {
  digitalWrite(RELE_1, 0);
  digitalWrite(RELE_2, 0);
  digitalWrite(RELE_3, 0);
  digitalWrite(RELE_4, 0);
  digitalWrite(RELE_5, 0);
  digitalWrite(RELE_6, 0);
  digitalWrite(RELE_7, 0);
  digitalWrite(RELE_8, 0);
  digitalWrite(RELE_9, 0);
  digitalWrite(RELE_10, 0);
  digitalWrite(RELE_11, 0);
  digitalWrite(RELE_12, 0);
  digitalWrite(RELE_13, 0);
  digitalWrite(RELE_14, 0);
  digitalWrite(RELE_15, 0);
  digitalWrite(RELE_16, 0);
}
