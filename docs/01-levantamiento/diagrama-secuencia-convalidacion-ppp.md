# Diagrama de Secuencia — Convalidación de Prácticas Preprofesionales (PPP)

Basado en el flujo "Requisitos para Convalidación de Prácticas Preprofesionales".

```mermaid
sequenceDiagram
    actor E as Estudiante (VII Ciclo)
    participant PA as P.A. de Ingeniería de Sistemas
    participant C as Comisión de PPP
    participant FI as Facultad de Ingeniería

    Note over E: Plazo: 20 días máximo<br/>para presentar el Informe de PPP

    E->>PA: Solicita convalidación en el sistema UDH
    E->>PA: Envía requisitos al correo institucional<br/>(solicitud, constancias de trabajo,<br/>boletas de pago, ficha de evaluación,<br/>informe técnico - Anexo 09)

    PA->>PA: Recepciona y verifica conformidad<br/>de los requisitos
    PA->>C: Deriva expediente a la Comisión de PPP

    C->>C: Evalúa el expediente de convalidación
    C->>C: Evalúa la sustentación de convalidación
    C-->>PA: Aprueba y emite constancia<br/>de aprobación de la PPP

    PA->>PA: Recepciona informe de la Comisión de PPP
    PA->>FI: Eleva el expediente aprobado

    FI->>FI: Recepciona requisitos del<br/>Informe Final de PPP
    FI-->>E: Aprueba mediante RESOLUCIÓN
```

## Notas del proceso
- La convalidación excepcional aplica a quien acredite fehacientemente haber laborado (nombrado o contratado, público o privado) en labores vinculadas a la especialidad, con mínimo el sexto ciclo concluido, por no menos de 16 meses.
- El expediente requiere el visto bueno de la Comisión de Práctica Preprofesional.
