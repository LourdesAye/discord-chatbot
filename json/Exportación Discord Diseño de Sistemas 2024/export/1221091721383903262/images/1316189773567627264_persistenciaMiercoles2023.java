@MappedSuperclass
public abstract class Persistente {
@Id  @GeneratedValue 
private Long id;
}

@Entity @Table(name”Deportista”)
class Deportista extends Persistente{
	@Column(name = "altura") 
private Double altura;
@Column(name = "apellido") 
private String apellido;
@Convert(converter = MotivacionConverter.class)
@Column(name = "motivacionPrincipal")
 	private Motivacion motivacionPrincipal;
@Column(name = "nombre") 
private String nombre;
@Column(name = "pesoInicial") 
private Double pesoInicial;
}

@Entity @Table(name”Rutina”)
class Rutina extends Persistente{
	@ManyToOne
@JoinColumn(name="id_deportista",referencedColumnName="id")
private Deportista deportista; 
@OneToMany
@JoinColumn(name="id_dia_entren", referencedColumnName = "id")
private List<DiaDeEntrenamiento> dias;
@OneToOne
@JoinColumn(name = "id_rutina_ant", referencedColumnName = "id")
private Rutina rutinaAnterior;
}

@Entity @Table(name”DiaDeEntrenamiento”)
class DiaDeEntrenamiento extends Persistente{
	@ManyToMany 
	@JoinTable(
	         name=”EjercicioPorDia”,
	         joinColumns=@JoinColumn(name=”id_dia_entren”,
	         referecedColumnName=”id”),
	        inverseJoinColumns=@JoinColumn(name=”id_ejercicio”,
	         referencedColumnName=”id”)
	)
	private List<Ejercicio> ejercicios; 
	@Column(name = "numero") 
private Integer numero;
@OneToOne
@JoinColumn(name = "id_sig_dia", referencedColumnName = "id")
private DiaDeEntrenamiento siguienteDia;
}

@Entity @Table(name”Ejercicio”)
class Ejercicio extends Persistente{
	@Column(name = "detalle") 
private String detalle;
@Column(name = "nombre") 
private String nombre;
}



