#define RELE_9 31

void setup() {
  Serial.begin(9600);  // Comunicación serial a 9600 baudios
  pinMode(RELE_9, OUTPUT);
  digitalWrite(RELE_9, HIGH);  // Apagar el rele (activo en LOW)
}

void loop() {
  if (Serial.available() > 0) {
    char mensaje[20];  // Asegúrate de que el tamaño del array es suficiente para el mensaje esperado
    Serial.readBytesUntil('\n', mensaje, sizeof(mensaje));
    procesar_mensaje(mensaje);
  }
}

// Procesa el mensaje recibido
void procesar_mensaje(char* mensaje) {
  // El mensaje tiene el formato "%,mesa_id,estado"
  if (mensaje[0] == '%') {
    // Extrae mesa_id y estado
    int mesa_id, estado;
    sscanf(mensaje, "%%,%d,%d", &mesa_id, &estado);

    Serial.print("Mensaje recibido: mesa ");
    Serial.print(mesa_id);
    Serial.print(", estado ");
    Serial.println(estado);

    if (estado == 1) {
      Serial.print("Encendiendo mesa: ");
      Serial.println(mesa_id);
      encender_rele(mesa_id);
    } else if (estado == 0) {
      Serial.print("Apagando mesa: ");
      Serial.println(mesa_id);
      apagar_rele(mesa_id);
    }
  }
}

// Enciende el rele correspondiente a la mesa
void encender_rele(int mesa) {
  switch (mesa) {
    case 1: digitalWrite(RELE_1, HIGH); break;
    case 2: digitalWrite(RELE_2, HIGH); break;
    case 3: digitalWrite(RELE_3, HIGH); break;
    case 4: digitalWrite(RELE_4, HIGH); break;
    case 5: digitalWrite(RELE_5, HIGH); break;
    case 6: digitalWrite(RELE_6, HIGH); break;
    case 7: digitalWrite(RELE_7, HIGH); break;
    case 8: digitalWrite(RELE_8, HIGH); break;
    case 9: digitalWrite(RELE_9, LOW); break;  // Encender RELE_9
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

// Apaga el rele correspondiente a la mesa
void apagar_rele(int mesa) {
  switch (mesa) {
    case 1: digitalWrite(RELE_1, LOW); break;
    case 2: digitalWrite(RELE_2, LOW); break;
    case 3: digitalWrite(RELE_3, LOW); break;
    case 4: digitalWrite(RELE_4, LOW); break;
    case 5: digitalWrite(RELE_5, LOW); break;
    case 6: digitalWrite(RELE_6, LOW); break;
    case 7: digitalWrite(RELE_7, LOW); break;
    case 8: digitalWrite(RELE_8, LOW); break;
    case 9: digitalWrite(RELE_9, HIGH); break;  // Apagar RELE_9
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
