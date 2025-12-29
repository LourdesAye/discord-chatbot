# Lista de autores docentes
autores_docentes = [
    ('ezequieloescobar', True),
    ('aylenmsandoval', True),
    ('lucassaclier', True),
    ('facuherrera_8', True),
    ('ryan129623', True),
    ('facundopiaggio', True),
    ('valentinaalberio', True),
    ('nacho_borda', True),
]

# Generamos la cantidad de placeholders dinámicamente
placeholders = ', '.join(['(%s, %s)'] * len(autores_docentes))