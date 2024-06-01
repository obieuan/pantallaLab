#define RELE_9 31

void setup() {
  Serial.begin(9600);  // Comunicacion serial a 9600 baudios
  pinMode(RELE_9, OUTPUT);
  digitalWrite(RELE_9, HIGH);  // Apagar el rele (activo en LOW)
}

void loop() {
  if (Serial.available() > 0) {
    char dato = Serial.read();
    if (dato == '1') {
      digitalWrite(RELE_9, LOW);  // Encender el rele (activo en LOW)
      Serial.println("Rele 9 encendido");
    } else if (dato == '0') {
      digitalWrite(RELE_9, HIGH);  // Apagar el rele (activo en LOW)
      Serial.println("Rele 9 apagado");
    }
  }
}
