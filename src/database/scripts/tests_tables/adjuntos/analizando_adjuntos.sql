-- por cada tipo de archivo, indica la cantidad
select lower(tipo), count(*)
from adjuntos
group by lower(tipo)

--select * from adjuntos