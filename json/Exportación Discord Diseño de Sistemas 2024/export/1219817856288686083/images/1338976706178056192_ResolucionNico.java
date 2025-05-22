//Interfaz implementada por clases concretas stateless => converter

public interface MedioDeNotificacion {
    public void enviarMensaje(Contacto contacto, Mensaje mensaje);
}

public class Wpp implements medioDeNotificacion {
    @Override
    public void enviarMensaje(Contacto contacto, Mensaje mensaje){
        //definition
    }
}
public class Sms implements medioDeNotificacion {
    @Override
    public void enviarMensaje(Contacto contacto, Mensaje mensaje){
        //definition
    }
}
public class Mail implements medioDeNotificacion {
    @Override
    public void enviarMensaje(Contacto contacto, Mensaje mensaje){
        //definition
    }
}

//Converter
@Converter(autoApply = true)
public class medioNotificacionConverter implements attributeConverter <MedioDeNotificacion, String>{
    //Proceso mapeo
    @Override 
    public String convertToDbCol(MedioDeNotificacion medio){
        if(medio instanceof Wpp){
            return "wpp"
        }
        if(medio instanceof Sms){
            return "sms"
        } 
        if(medio instanceof Mail){
            return "mail"
        }
        return null
    } 

    //Proceso hidratacion
    @Override
    public MedioDeNotificacion toEntity (String dbData){
        if("wpp".equals(dbData)){
            return new Wpp()
        }
        if("sms".equals(dbData)){
            return new Sms()
        }
        if("mail".equals(dbData)){
            return new Mail()
        }
        return null
    }

}

//Clase Persona
@Entity
@Table (name = Persona)
public class Persona {
    @Id
    @GeneratedValue
    private String id

    @Column
    private String nombre

    @Column
    private String apellido

    @Column
    private LocalDate fechaNacimiento

    @Column
    @Converter( converter = medioNotificacionConverter.class)
    private MedioDeNotificacion medioNotificacion

    @Column(nullable = true)
    private Integer nroCliente 

    @Column(nullable = true)
    private LocalDate fechaAlta

    @Column(nullable = true)
    @OneToMany(mappedBy = "persona")
    private List<DiaSemanaHorario> horarios;

    @Column
    private String tipoPersona
}

@Entity
@Table (name = Persona)
public class DiaSemanaHorario {
    @Id
    @GeneratedValue
    private String id

    @Column
    @Enumerated(EnumType.STRING)
    private DiaSemana dia

    @Column
    @ManyToOne
    @JoinColumn(name = "persona_id")
    private Persona persona

    @Column
    private String horaEntrada

    @Column
    private String horaSalida
}

public enum diaSemana {
    LUNES,
    MARTES,
    MIERCOLES,
    JUEVES,
    VIERNES
}




