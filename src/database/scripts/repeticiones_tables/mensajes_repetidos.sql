SELECT contenido,COUNT(*) AS conteo
FROM mensajes
GROUP BY contenido
HAVING COUNT(*) > 1
order by count(*) desc