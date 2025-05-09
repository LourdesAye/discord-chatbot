select lower(tipo), count(*)
from adjuntos
group by lower(tipo)

--select * from adjuntos